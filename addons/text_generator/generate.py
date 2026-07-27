import argparse
import sys
import os
import re
from src.load_model import get_model
from src.config import DEFAULT_PARAMS

def get_paraphrase_prompt(input_text, variants, target_language, level, style, genre, form, length, topic):
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "paraphrase.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(
        input_text=input_text,
        variants=variants,
        target_language=target_language,
        level=level,
        style=style,
        genre=genre,
        form=form,
        length=length,
        topic=topic
    )

def generate_text(args):
    model = get_model()
    
    # Use topic as the core keyword/concept if input_text is empty
    input_text = args.input_text or ""
    topic = args.topic or ""
    
    user_prompt = get_paraphrase_prompt(
        input_text=input_text,
        variants=args.variants,
        target_language=args.target_language,
        level=args.level,
        style=args.style,
        genre=args.genre,
        form=args.form,
        length=args.length,
        topic=topic
    )
    
    # Add an explicit instruction to continue after thinking
    response = model.create_chat_completion(
        messages=[
            {"role": "user", "content": user_prompt + "\n\nContinue immediately after </think> with the generated variations."}
        ],
        temperature=0.7,
        max_tokens=1024, # Increased to allow space for thinking + text
        top_p=DEFAULT_PARAMS["top_p"]
    )

    text = response['choices'][0]['message']['content']
    
    # Keep the content after the thinking process, if it exists
    if "</think>" in text:
        text = text.split("</think>")[-1]
    
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="Companion Text Generator CLI")
    parser.add_argument("--topic", help="Topic for text generation")
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--input-text", help="Input text for paraphrasing")
    parser.add_argument("--level", default="A2", help="Language level")
    parser.add_argument("--variants", type=int, default=1, help="Number of variants")
    parser.add_argument("--style", default="conversation", help="Style")
    parser.add_argument("--genre", default="general", help="Genre")
    parser.add_argument("--form", default="dialogue", help="Form")
    parser.add_argument("--length", default="short", help="Length")
    parser.add_argument("--target-language", default="nl", help="Target language")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not args.topic and not args.input and not args.input_text:
        parser.error("You must provide either --topic, --input, or --input-text")
        
    if args.verbose:
        sys.stderr.write("Generating variants...\n")
        
    text = generate_text(args)
    
    if args.output:
        # Use utf-8-sig for Windows compatibility (BOM)
        with open(args.output, "w", encoding="utf-8-sig") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        if args.verbose:
            sys.stderr.write(f"Variants saved to {args.output}\n")
    else:
        print(text)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
