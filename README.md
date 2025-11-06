# Dutch Word Analyzer

An AI agent tool for reading dutch books using Wiktionary API

- **Word meanings** (definitions from Wiktionary)
- **Grammatical forms** with accurate irregular verb handling:
  - **Verbs**: Past tense, Past participle
  - **Adjectives**: Comparative, Superlative
  - **Nouns**: Plural forms

## Usage

1. **Words file**: Create a text file with one Dutch word per line (each word followed by a '\n').

   Example `words.txt`:

   ```
   lezen
   schrijven
   begrijpen
   mooi
   groot
   ```

2. **Run the script**:

   ```bash
   python dutch_word_analyzer.py words.txt
   ```

3. **Optional: Save results to JSON**:
   ```bash
   python dutch_word_analyzer.py words.txt output.json
   ```

## Requirements

Install required packages:

**Option 1: Using a virtual environment (recommended)**

```bash
cd nederlands
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## How It Works

1. **Word Type Detection**: The script first determines if a word is a verb, noun, or adjective
2. **Irregular Verb Handling**: Checks against a built-in dictionary of ~30 common irregular verbs (including lezen, schrijven, begrijpen, komen, gaan, etc.)
3. **API Lookup**: Fetches meanings and forms from Wiktionary API
4. **HTML Parsing**: As a fallback, attempts to parse Dutch Wiktionary pages for conjugation tables
5. **Pattern Inference**: For regular verbs and other words, uses linguistic patterns to infer forms
6. **Form Filtering**: Removes inappropriate forms (e.g., verbs don't get comparative/superlative)

## Example Output

```
1. LEZEN
--------------------------------------------------------------------------------
Type: Verb
Meanings:
  • to read
  • to gather (esp. fruits)
Forms:
  Past Tense: las
  Past Participle: gelezen
```

## Notes

- **Accuracy**: Irregular verbs in the built-in dictionary are highly accurate. For verbs not in the dictionary, the script uses pattern-based inference which may need verification for irregular verbs.
- **API Rate Limiting**: The script includes a small delay between API calls to be respectful to the API servers
- **Adding Irregular Verbs**: You can add more irregular verbs to the `IRREGULAR_VERBS` dictionary in the script if needed
