"""
Holly's Closet — Flask backend for Railway deployment.

All Cloudinary credentials live in environment variables (set in Railway dashboard):
  CLOUDINARY_CLOUD_NAME
  CLOUDINARY_API_KEY
  CLOUDINARY_API_SECRET
  CHATRO_CODE      (optional default)
  UNDERGROUND_CODE (optional default)
  AVAILABLE_TAGS   (optional, comma-separated)
  APP_SECRET_KEY   (random string for session signing)
"""

import os
import re
import json

import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import Flask, jsonify, request, render_template, session

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "dev-secret-change-me")

# ── Cloudinary config ──────────────────────────────────────────
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)

# ── Default snippet codes & tags (overridable via env) ─────────
DEFAULT_CHATRO_CODE    = os.environ.get("CHATRO_CODE", "[img]SNIPPET[/img][color #a0a0a0]holly~.[/color]")
DEFAULT_UNDERGROUND    = os.environ.get("UNDERGROUND_CODE", '<img src="SNIPPET"> holly~.')
DEFAULT_TAGS_RAW       = os.environ.get("AVAILABLE_TAGS", "Favorites,Lair,LoL,Naked Nights,Tushday,Hickies,Parties")
DEFAULT_TAGS           = [t.strip() for t in DEFAULT_TAGS_RAW.split(",") if t.strip()]


# ── Natural sort helper ────────────────────────────────────────
def _natural_key(s):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'([0-9]+)', s)]


def sort_resources(resources):
    favorites, others, parties = [], [], []
    for r in resources:
        tags = r.get("tags") or []
        if "Favorites" in tags:
            favorites.append(r)
        elif "Parties" in tags:
            parties.append(r)
        else:
            others.append(r)
    key = lambda r: _natural_key(r["public_id"])
    return sorted(favorites, key=key) + sorted(others, key=key) + sorted(parties, key=key)


# ── Session-persisted settings helpers ────────────────────────
def get_chatro():
    return session.get("chatro_code", DEFAULT_CHATRO_CODE)

def get_underground():
    return session.get("underground_code", DEFAULT_UNDERGROUND)

def get_tags():
    return session.get("available_tags", list(DEFAULT_TAGS))


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Images ────────────────────────────────────────────────────

@app.route("/api/images")
def api_images():
    try:
        resp = cloudinary.api.resources(
            type="upload",
            max_results=500,
            tags=True,
        )
        resources = resp.get("resources", [])
        sorted_resources = sort_resources(resources)
        # Return minimal payload — frontend only needs these fields
        out = []
        for r in sorted_resources:
            out.append({
                "public_id":  r.get("public_id"),
                "secure_url": r.get("secure_url") or r.get("url"),
                "tags":       r.get("tags") or [],
                "format":     r.get("format", "jpg"),
                "created_at": r.get("created_at", ""),
                "version":    r.get("version"),
            })
        return jsonify({"images": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/images/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    public_id = request.form.get("public_id") or os.path.splitext(f.filename)[0]
    try:
        result = cloudinary.uploader.upload(f, public_id=public_id, tags=[])
        return jsonify({
            "public_id":  result.get("public_id"),
            "secure_url": result.get("secure_url"),
            "tags":       [],
            "format":     result.get("format", "jpg"),
            "created_at": result.get("created_at", ""),
            "version":    result.get("version"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/images/<path:public_id>/delete", methods=["POST"])
def api_delete(public_id):
    try:
        cloudinary.uploader.destroy(public_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/images/<path:public_id>/rename", methods=["POST"])
def api_rename(public_id):
    data = request.get_json(silent=True) or {}
    new_id = data.get("new_id", "").strip()
    if not new_id:
        return jsonify({"error": "new_id required"}), 400
    try:
        result = cloudinary.uploader.rename(public_id, new_id)
        return jsonify({
            "public_id":  result.get("public_id"),
            "secure_url": result.get("secure_url"),
            "version":    result.get("version"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/images/<path:public_id>/tags", methods=["POST"])
def api_set_tags(public_id):
    data = request.get_json(silent=True) or {}
    tags = data.get("tags", [])
    try:
        # Replace all tags on the resource
        if tags:
            cloudinary.uploader.replace_tag(",".join(tags), [public_id])
        else:
            cloudinary.uploader.remove_all_tags([public_id])
        return jsonify({"ok": True, "tags": tags})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Settings (codes, tags) — stored in server session ─────────

@app.route("/api/settings", methods=["GET"])
def api_settings_get():
    return jsonify({
        "chatro_code":    get_chatro(),
        "underground_code": get_underground(),
        "available_tags": get_tags(),
    })


@app.route("/api/settings", methods=["POST"])
def api_settings_save():
    data = request.get_json(silent=True) or {}
    if "chatro_code" in data:
        session["chatro_code"] = data["chatro_code"]
    if "underground_code" in data:
        session["underground_code"] = data["underground_code"]
    if "available_tags" in data:
        tags = [str(t).strip() for t in data["available_tags"] if str(t).strip()]
        session["available_tags"] = tags
    return jsonify({
        "chatro_code":    get_chatro(),
        "underground_code": get_underground(),
        "available_tags": get_tags(),
    })


# ── Health check ───────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
