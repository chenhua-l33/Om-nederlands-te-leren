#!/usr/bin/env python3
"""
Dutch Word Analyzer - AI Agent
Processes Dutch words from a text file and provides meanings and various forms.
"""

import requests
import json
import time
import sys
import re
from typing import Dict, List, Optional
from pathlib import Path


class DutchWordAnalyzer:
    """AI agent to analyze Dutch words and provide meanings and forms."""
    
    # Common irregular Dutch verbs: {infinitive: (past_tense, past_participle)}
    IRREGULAR_VERBS = {
        'lezen': ('las', 'gelezen'),
        'schrijven': ('schreef', 'geschreven'),
        'begrijpen': ('begreep', 'begrepen'),
        'komen': ('kwam', 'gekomen'),
        'gaan': ('ging', 'gegaan'),
        'zien': ('zag', 'gezien'),
        'doen': ('deed', 'gedaan'),
        'hebben': ('had', 'gehad'),
        'zijn': ('was', 'geweest'),
        'worden': ('werd', 'geworden'),
        'nemen': ('nam', 'genomen'),
        'geven': ('gaf', 'gegeven'),
        'blijven': ('bleef', 'gebleven'),
        'krijgen': ('kreeg', 'gekregen'),
        'zeggen': ('zei', 'gezegd'),
        'weten': ('wist', 'geweten'),
        'eten': ('at', 'gegeten'),
        'drinken': ('dronk', 'gedronken'),
        'lopen': ('liep', 'gelopen'),
        'staan': ('stond', 'gestaan'),
        'zitten': ('zat', 'gezeten'),
        'liggen': ('lag', 'gelegen'),
        'vinden': ('vond', 'gevonden'),
        'denken': ('dacht', 'gedacht'),
        'brengen': ('bracht', 'gebracht'),
        'kopen': ('kocht', 'gekocht'),
        'verkopen': ('verkocht', 'verkocht'),
        'helpen': ('hielp', 'geholpen'),
        'spreken': ('sprak', 'gesproken'),
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://api.woordenboek.nl/api/v1"
        
    def get_word_info(self, word: str) -> Dict:
        """
        Get word information including meaning and forms.
        Uses multiple sources for comprehensive data.
        """
        word = word.strip().lower()
        if not word:
            return {}
            
        result = {
            'word': word,
            'meanings': [],
            'forms': {
                'past_tense': None,
                'past_participle': None,
                'present_tense': None,
                'plural': None,
                'comparative': None,
                'superlative': None
            },
            'word_type': None
        }
        
        # Try to get information from Wiktionary
        wiktionary_data = self._get_wiktionary_info(word)
        if wiktionary_data:
            result.update(wiktionary_data)
        
        # Try to get information from Woordenboek.nl API
        woordenboek_data = self._get_woordenboek_info(word)
        if woordenboek_data:
            if not result['meanings']:
                result['meanings'] = woordenboek_data.get('meanings', [])
            if not result['word_type']:
                result['word_type'] = woordenboek_data.get('word_type')
            # Merge forms
            for key in result['forms']:
                if not result['forms'][key] and woordenboek_data.get('forms', {}).get(key):
                    result['forms'][key] = woordenboek_data['forms'][key]
        
        return result
    
    def _get_wiktionary_info(self, word: str) -> Optional[Dict]:
        """Get word information from Wiktionary."""
        try:
            # Try to get definitions
            url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
            response = self.session.get(url, timeout=5)
            
            result = {
                'meanings': [],
                'forms': {},
                'word_type': None
            }
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract Dutch definitions
                if 'nl' in data:
                    nl_data = data['nl']
                    for entry in nl_data:
                        # Get word type
                        if not result['word_type'] and 'partOfSpeech' in entry:
                            result['word_type'] = entry['partOfSpeech']
                        
                        # Get meanings
                        if 'definitions' in entry:
                            for definition in entry['definitions']:
                                if 'definition' in definition:
                                    meaning = definition['definition']
                                    # Clean HTML tags from meaning
                                    meaning = re.sub(r'<[^>]+>', '', meaning)
                                    meaning = meaning.strip()
                                    if meaning:
                                        result['meanings'].append(meaning)
            
            # Try to get inflections/forms from a different endpoint
            try:
                inflections_url = f"https://en.wiktionary.org/api/rest_v1/page/inflections/{word}"
                infl_response = self.session.get(inflections_url, timeout=5)
                if infl_response.status_code == 200:
                    try:
                        infl_data = infl_response.json()
                        if 'nl' in infl_data:
                            nl_infl = infl_data['nl']
                            for entry in nl_infl:
                                if 'inflectionOf' in entry:
                                    for infl in entry['inflectionOf']:
                                        if 'features' in infl:
                                            features = infl['features']
                                            infl_word = infl.get('word', '')
                                            
                                            # Past tense
                                            if 'tense' in features and features['tense'] == 'past':
                                                if 'number' in features and features['number'] == 'singular':
                                                    result['forms']['past_tense'] = infl_word
                                            
                                            # Past participle
                                            if 'aspect' in features and features['aspect'] == 'perfect':
                                                result['forms']['past_participle'] = infl_word
                                            
                                            # Plural
                                            if 'number' in features and features['number'] == 'plural':
                                                result['forms']['plural'] = infl_word
                                            
                                            # Comparative
                                            if 'degree' in features and features['degree'] == 'comparative':
                                                result['forms']['comparative'] = infl_word
                                            
                                            # Superlative
                                            if 'degree' in features and features['degree'] == 'superlative':
                                                result['forms']['superlative'] = infl_word
                    except:
                        pass
            except:
                pass  # Inflections endpoint might not be available
            
            # Check if it's a known irregular verb (check this early)
            if word in self.IRREGULAR_VERBS:
                past_tense, past_participle = self.IRREGULAR_VERBS[word]
                # Set word type to verb if not already set
                if not result.get('word_type'):
                    result['word_type'] = 'verb'
                # Always use irregular forms (they override any pattern-based inference)
                result['forms']['past_tense'] = past_tense
                result['forms']['past_participle'] = past_participle
            
            # Try to parse the actual Wiktionary page HTML for conjugation tables
            try:
                page_url = f"https://nl.wiktionary.org/wiki/{word}"
                page_response = self.session.get(page_url, timeout=5)
                if page_response.status_code == 200:
                    html_content = page_response.text
                    # Look for past tense in conjugation table - more flexible pattern
                    # Try multiple patterns
                    patterns = [
                        r'verleden tijd[^<]*?<td[^>]*>([^<]+)</td>',
                        r'imperfectum[^<]*?<td[^>]*>([^<]+)</td>',
                        r'<th[^>]*>verleden tijd</th>[^<]*?<td[^>]*>([^<]+)</td>',
                    ]
                    for pattern in patterns:
                        past_tense_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                        if past_tense_match and not result['forms'].get('past_tense'):
                            past_form = past_tense_match.group(1).strip()
                            # Clean up the form
                            past_form = re.sub(r'<[^>]+>', '', past_form)  # Remove any HTML tags
                            past_form = re.sub(r'\s+', ' ', past_form).split()[0] if past_form else None
                            if past_form and len(past_form) > 1:
                                result['forms']['past_tense'] = past_form
                                break
                    
                    # Look for past participle (voltooid deelwoord)
                    part_patterns = [
                        r'voltooid deelwoord[^<]*?<td[^>]*>([^<]+)</td>',
                        r'perfectum[^<]*?<td[^>]*>([^<]+)</td>',
                        r'<th[^>]*>voltooid deelwoord</th>[^<]*?<td[^>]*>([^<]+)</td>',
                    ]
                    for pattern in part_patterns:
                        participle_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                        if participle_match and not result['forms'].get('past_participle'):
                            part_form = participle_match.group(1).strip()
                            part_form = re.sub(r'<[^>]+>', '', part_form)
                            part_form = re.sub(r'\s+', ' ', part_form).split()[0] if part_form else None
                            if part_form and len(part_form) > 1:
                                result['forms']['past_participle'] = part_form
                                break
            except Exception as e:
                pass  # HTML parsing might fail
            
            return result if result['meanings'] or any(result['forms'].values()) else None
        except Exception as e:
            print(f"  Warning: Could not fetch from Wiktionary: {e}", file=sys.stderr)
        
        return None
    
    def _get_woordenboek_info(self, word: str) -> Optional[Dict]:
        """Get word information from Woordenboek.nl (fallback method)."""
        # This is a placeholder - you might need to use a different API
        # or implement web scraping if needed
        return None
    
    def _get_verb_forms(self, word: str) -> Dict:
        """Get verb forms (conjugations) for Dutch verbs."""
        forms = {}
        
        # Common Dutch verb patterns
        if word.endswith('en'):
            stem = word[:-2]
            if len(stem) > 0:
                # Determine if verb is weak (regular) or strong (irregular)
                # For weak verbs: past tense ends in -de or -te, past participle in ge-...-d or ge-...-t
                
                # Check final consonant of stem
                final_cons = stem[-1].lower() if stem else ''
                
                # Dutch spelling rule: if stem ends in voiceless consonant (p, t, k, f, s, ch), use -te
                # Otherwise use -de
                voiceless = final_cons in ['p', 't', 'k', 'f', 's', 'x', 'c']
                
                # Past tense (simple past, singular)
                if voiceless:
                    forms['past_tense'] = stem + 'te'
                else:
                    forms['past_tense'] = stem + 'de'
                
                # Past participle: ge- + stem + -d or -t
                if voiceless:
                    forms['past_participle'] = 'ge' + stem + 't'
                else:
                    forms['past_participle'] = 'ge' + stem + 'd'
        
        return forms
    
    def _get_noun_forms(self, word: str) -> Dict:
        """Get noun forms (plural) for Dutch nouns."""
        forms = {}
        
        # Common Dutch plural patterns
        if word.endswith('el') or word.endswith('er') or word.endswith('en'):
            forms['plural'] = word + 's'
        elif word.endswith('heid'):
            forms['plural'] = word + 'en'
        elif word.endswith('ing'):
            forms['plural'] = word + 'en'
        else:
            forms['plural'] = word + 'en'  # Most common pattern
        
        return forms
    
    def _get_adjective_forms(self, word: str) -> Dict:
        """Get adjective forms (comparative and superlative) for Dutch adjectives."""
        forms = {}
        
        # Dutch comparative: -er, superlative: -st
        # For most adjectives ending in a consonant
        if len(word) > 2:
            # Comparative
            forms['comparative'] = word + 'er'
            
            # Superlative
            if word.endswith('r'):
                forms['superlative'] = word + 'st'
            else:
                forms['superlative'] = word + 'st'
        
        return forms
    
    def process_words_from_file(self, file_path: str) -> List[Dict]:
        """Process words from a text file (one word per line)."""
        words_file = Path(file_path)
        
        if not words_file.exists():
            print(f"Error: File '{file_path}' not found.", file=sys.stderr)
            return []
        
        # Read words from file
        with open(words_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        
        print(f"Found {len(words)} words to process...\n")
        
        results = []
        for i, word in enumerate(words, 1):
            print(f"Processing [{i}/{len(words)}]: {word}...", end=' ', flush=True)
            word_info = self.get_word_info(word)
            
            # If no API data, try to infer forms based on word patterns
            # Determine word type first, then only add appropriate forms
            word_type = word_info.get('word_type', '').lower()
            
            # Don't use pattern-based inference if it's a known irregular verb
            is_irregular = word in self.IRREGULAR_VERBS
            
            if not word_type or not any(word_info['forms'].values()):
                # Try to infer verb forms (but skip if it's irregular - already handled)
                if not is_irregular:
                    verb_forms = self._get_verb_forms(word)
                    if verb_forms and any(verb_forms.values()):
                        if not word_type:
                            word_type = 'verb'
                            word_info['word_type'] = 'verb'
                        if word_type == 'verb':
                            for key, value in verb_forms.items():
                                if not word_info['forms'].get(key):
                                    word_info['forms'][key] = value
                elif is_irregular and not word_type:
                    # Mark as verb if it's irregular
                    word_type = 'verb'
                    word_info['word_type'] = 'verb'
                
                # Try to infer noun forms
                noun_forms = self._get_noun_forms(word)
                if noun_forms and not word_type:
                    word_type = 'noun'
                    word_info['word_type'] = 'noun'
                if word_type == 'noun':
                    if noun_forms and not word_info['forms'].get('plural'):
                        word_info['forms']['plural'] = noun_forms.get('plural')
                
                # Try to infer adjective forms
                adj_forms = self._get_adjective_forms(word)
                if adj_forms and not word_type:
                    word_type = 'adjective'
                    word_info['word_type'] = 'adjective'
                if word_type == 'adjective':
                    for key, value in adj_forms.items():
                        if not word_info['forms'].get(key):
                            word_info['forms'][key] = value
            
            # Clean up inappropriate forms based on word type
            word_type = word_info.get('word_type', '').lower()
            if word_type == 'verb':
                # Verbs should not have comparative, superlative, or plural
                word_info['forms']['comparative'] = None
                word_info['forms']['superlative'] = None
                word_info['forms']['plural'] = None
            elif word_type == 'adjective':
                # Adjectives should not have past_tense, past_participle, present_tense, or plural
                word_info['forms']['past_tense'] = None
                word_info['forms']['past_participle'] = None
                word_info['forms']['present_tense'] = None
                word_info['forms']['plural'] = None
            elif word_type == 'noun':
                # Nouns should not have verb forms or adjective forms
                word_info['forms']['past_tense'] = None
                word_info['forms']['past_participle'] = None
                word_info['forms']['present_tense'] = None
                word_info['forms']['comparative'] = None
                word_info['forms']['superlative'] = None
            
            results.append(word_info)
            print("✓")
            
            # Be polite to APIs
            time.sleep(0.5)
        
        return results
    
    def display_results(self, results: List[Dict]):
        """Display results in a formatted way."""
        print("\n" + "="*80)
        print("DUTCH WORD ANALYSIS RESULTS")
        print("="*80 + "\n")
        
        for i, word_info in enumerate(results, 1):
            word = word_info.get('word', 'Unknown')
            print(f"{i}. {word.upper()}")
            print("-" * 80)
            
            # Word type
            if word_info.get('word_type'):
                print(f"Type: {word_info['word_type']}")
            
            # Meanings
            meanings = word_info.get('meanings', [])
            if meanings:
                print("Meanings:")
                for meaning in meanings[:3]:  # Show first 3 meanings
                    print(f"  • {meaning}")
            else:
                print("Meanings: (Not found - you may need to add manually)")
            
            # Forms - only show non-None values
            forms = word_info.get('forms', {})
            # Filter out None values
            valid_forms = {k: v for k, v in forms.items() if v is not None}
            
            if valid_forms:
                print("Forms:")
                if valid_forms.get('past_tense'):
                    print(f"  Past Tense: {valid_forms['past_tense']}")
                if valid_forms.get('past_participle'):
                    print(f"  Past Participle: {valid_forms['past_participle']}")
                if valid_forms.get('present_tense'):
                    print(f"  Present Tense: {valid_forms['present_tense']}")
                if valid_forms.get('plural'):
                    print(f"  Plural: {valid_forms['plural']}")
                if valid_forms.get('comparative'):
                    print(f"  Comparative: {valid_forms['comparative']}")
                if valid_forms.get('superlative'):
                    print(f"  Superlative: {valid_forms['superlative']}")
                # Note about irregular verbs
                if word_info.get('word_type', '').lower() == 'verb' and not valid_forms.get('past_tense'):
                    print("  Note: This may be an irregular verb - forms may need verification")
            else:
                print("Forms: (Not found - may need manual lookup)")
            
            print()
    
    def save_results(self, results: List[Dict], output_file: str):
        """Save results to a JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {output_file}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python dutch_word_analyzer.py <words_file.txt> [output.json]")
        print("\nExample:")
        print("  python dutch_word_analyzer.py words.txt")
        print("  python dutch_word_analyzer.py words.txt output.json")
        sys.exit(1)
    
    words_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = DutchWordAnalyzer()
    results = analyzer.process_words_from_file(words_file)
    
    if results:
        analyzer.display_results(results)
        
        if output_file:
            analyzer.save_results(results, output_file)
    else:
        print("No words processed.")


if __name__ == "__main__":
    main()

