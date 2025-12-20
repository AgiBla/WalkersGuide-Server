"""
Translation Completeness Test Script

This script verifies that all translation functions contain the same
category/tag combinations to ensure no translations are missing.
"""

import sys
import inspect
from collections import defaultdict


# Import the Translator class
try:
    from webserver.translator import Translator
except ImportError:
    print("Error: Could not import Translator class.")
    sys.exit(1)


def extract_translations_from_function(func):
    """
    Extract all category/tag combinations from a translation function.
    
    Returns a dictionary: {category: set(tags)}
    """
    translations = defaultdict(set)
    
    # Get the source code of the function
    source = inspect.getsource(func)
    lines = source.split('\n')
    
    current_category = None
    
    for line in lines:
        line = line.strip()
        
        # Detect category check
        if line.startswith('if category == "'):
            current_category = line.split('"')[1]
        
        # Detect tag check and return statement
        if current_category and line.startswith('if tag ==') and 'return' in line:
            # Extract tag value
            tag_part = line.split('if tag ==')[1].split(':')[0].strip()
            
            # Handle simple tag check: if tag == "value"
            if tag_part.startswith('"'):
                tag = tag_part.strip('"')
                translations[current_category].add(tag)
            
            # Handle tag in list check: if tag in ["value1", "value2"]
            elif tag_part.startswith('['):
                # Extract all tags from the list
                tags_str = tag_part.strip('[]')
                tags = [t.strip().strip('"') for t in tags_str.split(',')]
                for tag in tags:
                    translations[current_category].add(tag)
    
    return translations


def compare_translations(lang1_name, lang1_trans, lang2_name, lang2_trans):
    """
    Compare two translation dictionaries and report differences.
    
    Returns True if they match, False otherwise.
    """
    all_categories = set(lang1_trans.keys()) | set(lang2_trans.keys())
    
    missing_in_lang1 = []
    missing_in_lang2 = []
    has_differences = False
    
    for category in sorted(all_categories):
        tags1 = lang1_trans.get(category, set())
        tags2 = lang2_trans.get(category, set())
        
        # Tags in lang2 but not in lang1
        missing_tags1 = tags2 - tags1
        if missing_tags1:
            has_differences = True
            for tag in sorted(missing_tags1):
                missing_in_lang1.append((category, tag))
        
        # Tags in lang1 but not in lang2
        missing_tags2 = tags1 - tags2
        if missing_tags2:
            has_differences = True
            for tag in sorted(missing_tags2):
                missing_in_lang2.append((category, tag))
    
    if has_differences:
        if missing_in_lang1:
            print(f"\n Missing in {lang1_name}:")
            for category, tag in missing_in_lang1:
                print(f"   Category: '{category}', Tag: '{tag}'")
        
        if missing_in_lang2:
            print(f"\n Missing in {lang2_name}:")
            for category, tag in missing_in_lang2:
                print(f"   Category: '{category}', Tag: '{tag}'")
        
        return False
    
    return True


def print_translation_summary(lang_name, translations):
    """Print a summary of translations for a language."""
    total_tags = sum(len(tags) for tags in translations.values())
    print(f"\n{lang_name}:")
    print(f"  Categories: {len(translations)}")
    print(f"  Total tags: {total_tags}")
    
    for category in sorted(translations.keys()):
        print(f"    {category}: {len(translations[category])} tags")


def run_tests():
    print("=" * 70)
    print("Translation Completeness Test")
    print("=" * 70)
    
    # Create a Translator instance
    translator = Translator()
    
    # Get all translation functions
    translate_english = translator.translate_to_english
    translate_german = translator.translate_to_german
    translate_spanish = translator.translate_to_spanish
    translate_ukrainian = translator.translate_to_ukrainian
    
    print("\n Extracting translations from each function...")
    
    # Extract translations from each function
    english_trans = extract_translations_from_function(translate_english)
    german_trans = extract_translations_from_function(translate_german)
    spanish_trans = extract_translations_from_function(translate_spanish)
    ukrainian_trans = extract_translations_from_function(translate_ukrainian)
    
    # Print summaries
    print("\n" + "=" * 70)
    print("Translation Summary")
    print("=" * 70)
    
    print_translation_summary("English", english_trans)
    print_translation_summary("German", german_trans)
    print_translation_summary("Spanish", spanish_trans)
    print_translation_summary("Ukrainian", ukrainian_trans)
    
    # Compare all languages against English (as the reference)
    print("\n" + "=" * 70)
    print("Completeness Check (comparing against English)")
    print("=" * 70)
    
    all_match = True
    
    print("\nComparing German with English...")
    if compare_translations("German", german_trans, "English", english_trans):
        print(" German translations are complete!")
    else:
        all_match = False
    
    print("\nComparing Spanish with English...")
    if compare_translations("Spanish", spanish_trans, "English", english_trans):
        print(" Spanish translations are complete!")
    else:
        all_match = False
    
    print("\nComparing Ukrainian with English...")
    if compare_translations("Ukrainian", ukrainian_trans, "English", english_trans):
        print(" Ukrainian translations are complete!")
    else:
        all_match = False
    
    # Final result
    print("\n" + "=" * 70)
    if all_match:
        print("SUCCESS: All translations are complete and consistent!")
        print("=" * 70)
        return 0
    else:
        print("FAILURE: Some translations are missing or inconsistent!")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
