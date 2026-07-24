import argparse
import json
import os
from src.load_model import get_model
from src.config import DEFAULT_PARAMS

def generate_text(topic, level, count, style):
    model = get_model()
    
    results = []
    for i in range(count):
        prompt = f"Topic: {topic}\nLevel: {level}\nStyle: {style}\nGenerate a natural text variant for this situation.\n\n"
        
        response = model.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=DEFAULT_PARAMS["temperature"],
            max_tokens=DEFAULT_PARAMS["max_tokens"],
            top_p=DEFAULT_PARAMS["top_p"]
        )
        
        text = response['choices'][0]['message']['content']
        results.append(text)
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Companion Text Generator CLI")
    parser.add_argument("--topic", required=True, help="Topic for text generation")
    parser.add_argument("--level", default="A2", help="Language level")
    parser.add_argument("--count", type=int, default=1, help="Number of variants")
    parser.add_argument("--style", default="dialogue", help="Style (monologue, dialogue, etc.)")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    print(f"Generating {args.count} variants on '{args.topic}'...")
    variants = generate_text(args.topic, args.level, args.count, args.style)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for i, v in enumerate(variants):
                f.write(f"--- Variant {i+1} ---\n{v}\n\n")
        print(f"Variants saved to {args.output}")
    else:
        for i, v in enumerate(variants):
            print(f"\n--- Variant {i+1} ---\n{v}")

if __name__ == "__main__":
    main()
