from pathlib import Path

from backend.app.models.image_captioner import (
    caption_image_with_qwen_vl,
    get_lmstudio_client,
)


def main() -> None:
    # --- Projekt-Root sauber bestimmen ---
    project_root = Path(__file__).resolve().parents[1]
    print(f" Project root: {project_root}")
    image_path = project_root / "data" / "test_image.jpg"
    print(image_path)
    print(f"Project root: {project_root}")
    print(f"Expecting test image at: {image_path}")

    if not image_path.exists():
        print(" Test image not found!")
        print("Please place a file at: data/test_image.jpg")
        return

    # --- LM Studio Models checken ---
    try:
        client = get_lmstudio_client()
        models = client.models.list()

        print("\n Connected to LM Studio. Available models:")
        for m in models.data:
            print(f" - {m.id}")
    except Exception as e:
        print("\n Could not connect to LM Studio or list models.")
        print(f"Error: {e}")
        return

    # --- Bild laden ---
    image_bytes = image_path.read_bytes()
    print(f"\n Loaded image: {image_path.name} ({len(image_bytes)} bytes)")

    # --- Caption holen ---
    try:
        print("\n  Requesting caption from qwen/qwen3-vl-4b ...")
        caption = caption_image_with_qwen_vl(
            image_bytes=image_bytes,
            model="qwen/qwen3-vl-4b",  # Modellname aus LM Studio
            language="en",             # oder "de", wenn du lieber Deutsch willst
            max_tokens=512,
        )
        print("\n Caption received:\n")
        print(caption)
    except Exception as e:
        print("\n Error while generating caption:")
        print(repr(e))


if __name__ == "__main__":
    main()
