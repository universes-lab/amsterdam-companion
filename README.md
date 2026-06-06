# Amsterdam Companion

Telegram bot for learning Dutch.

## Setup

1. Copy `.env.example` to `.env` and fill in the values.
2. Install dependencies: `pip install -r requirements.txt`
3. **Important:** Convert translation model once:
   `python scripts/convert_nllb_ct2.py --model facebook/nllb-200-distilled-600M`
4. Run startup validation: `python -c "from diagnostics.startup_validator import validate_environment; validate_environment()"`

## Troubleshooting

- **ffmpeg not found:** Ensure `ffmpeg` is installed and in your system PATH.
- **Model not found:** Make sure you have run the conversion script in Step 3.
