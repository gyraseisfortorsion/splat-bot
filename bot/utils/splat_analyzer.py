"""SPLAT test file analyzer to generate questions"""
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple


class SplatTestAnalyzer:
    """Analyze SPLAT test files and generate quiz questions"""

    def __init__(self, tests_dir: str):
        self.tests_dir = Path(tests_dir)
        self.questions = []

    def get_exception_type(self, filename: str) -> Tuple[str, str]:
        """Determine exception type from filename"""
        if "_badlex" in filename:
            return "LexException", "lexer"
        elif "_badparse" in filename:
            return "ParseException", "parser"
        elif "_badsemantics" in filename:
            return "SemanticAnalysisException", "semantics"
        elif "_badexecution" in filename:
            return "ExecutionException", "executor"
        elif "_goodexecution" in filename:
            return "Success", "execution"
        return "Unknown", "unknown"

    def read_file(self, filepath: Path) -> str:
        """Read SPLAT file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""

    def generate_lex_question(self, filename: str, code: str) -> Dict:
        """Generate question for lex exception test"""
        # Analyze common lex errors
        if '{' in code:
            error_char = '{'
            reason = "SPLAT uses 'begin' and 'end' keywords, not braces"
        elif '!' in code and '!=' not in code:
            error_char = '!'
            reason = "SPLAT does not support '!' as a standalone operator"
        elif '\\' in code and '\\n' not in code and '\\t' not in code:
            error_char = '\\\\'
            reason = "Backslash is only valid in string escape sequences"
        elif '=' in code and ':=' not in code and '==' not in code:
            error_char = '='
            reason = "SPLAT uses ':=' for assignment, not '='"
        else:
            # Find invalid character
            valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_()[]{}:;,+-*/<>=!&| \t\n\"'")
            for char in code:
                if char not in valid_chars:
                    error_char = char
                    reason = f"'{char}' is not a valid character in SPLAT"
                    break
            else:
                error_char = "invalid"
                reason = "Contains invalid character sequence"

        # Check for unclosed strings
        if code.count('"') % 2 != 0:
            error_char = '"'
            reason = "String literal is not properly closed"

        question = {
            "category": "lexer",
            "subcategory": "badlex",
            "source_file": filename,
            "question_text": f"What exception does this SPLAT code throw?",
            "code": code.strip(),
            "option_a": "LexException - Invalid character",
            "option_b": "ParseException - Syntax error",
            "option_c": "SemanticAnalysisException - Type error",
            "option_d": "ExecutionException - Runtime error",
            "option_e": "No exception (executes successfully)",
            "correct_answer": "A",
            "explanation": f"This code throws a LexException because {reason}. The lexer (Phase 1) identifies individual tokens and catches invalid characters before parsing begins.",
            "difficulty": "easy"
        }
        return question

    def generate_parse_question(self, filename: str, code: str) -> Dict:
        """Generate question for parse exception test"""
        # Analyze common parse errors
        if "program" not in code.lower():
            reason = "missing 'program' keyword at the start"
        elif code.count("begin") != code.count("end"):
            reason = "mismatched 'begin' and 'end' keywords"
        elif ":=" not in code and "return" not in code and "print" not in code:
            reason = "invalid statement syntax"
        elif "(" in code and ")" in code and code.count("(") != code.count(")"):
            reason = "mismatched parentheses"
        else:
            reason = "violates SPLAT grammar rules"

        question = {
            "category": "parser",
            "subcategory": "badparse",
            "source_file": filename,
            "question_text": f"What exception does this SPLAT code throw?",
            "code": code.strip(),
            "option_a": "LexException - Invalid character",
            "option_b": "ParseException - Syntax error",
            "option_c": "SemanticAnalysisException - Type error",
            "option_d": "ExecutionException - Runtime error",
            "option_e": "No exception (executes successfully)",
            "correct_answer": "B",
            "explanation": f"This code throws a ParseException because it {reason}. The parser (Phase 2) builds an Abstract Syntax Tree and detects syntax errors that violate the grammar.",
            "difficulty": "medium"
        }
        return question

    def generate_semantic_question(self, filename: str, code: str) -> Dict:
        """Generate question for semantic exception test"""
        # Analyze common semantic errors
        if "not declared" in filename or "not defined" in filename:
            reason = "it references an undeclared variable or function"
        elif "type" in filename.lower():
            reason = "there's a type mismatch (e.g., assigning Integer to Boolean)"
        elif "duplicate" in filename.lower():
            reason = "it has duplicate variable/function declarations"
        elif "return" in code and "void" in code:
            reason = "a void function has a return value, or vice versa"
        else:
            # Try to detect from code
            lines = code.split('\n')
            if any(':=' in line and ('true' in line or 'false' in line) for line in lines):
                reason = "there's a type mismatch between Integer and Boolean"
            elif 'return' in code and any('Integer' in line or 'Boolean' in line for line in lines):
                reason = "the return type doesn't match the function declaration"
            else:
                reason = "it violates semantic rules like type checking or scope rules"

        question = {
            "category": "semantics",
            "subcategory": "badsemantics",
            "source_file": filename,
            "question_text": f"What exception does this SPLAT code throw?",
            "code": code.strip(),
            "option_a": "LexException - Invalid character",
            "option_b": "ParseException - Syntax error",
            "option_c": "SemanticAnalysisException - Type/scope error",
            "option_d": "ExecutionException - Runtime error",
            "option_e": "No exception (executes successfully)",
            "correct_answer": "C",
            "explanation": f"This code throws a SemanticAnalysisException because {reason}. The semantic analyzer (Phase 3) performs type checking and validates scope rules after parsing.",
            "difficulty": "medium"
        }
        return question

    def generate_execution_question(self, filename: str, code: str) -> Dict:
        """Generate question for execution exception test"""
        reason = "it attempts division by zero"
        if "/ 0" in code or "% 0" in code:
            reason = "it explicitly divides or uses modulus by zero"
        elif "Height" in code and ":= 0" in code:
            reason = "it divides by an uninitialized variable (default value 0)"

        question = {
            "category": "executor",
            "subcategory": "badexecution",
            "source_file": filename,
            "question_text": f"What exception does this SPLAT code throw?",
            "code": code.strip(),
            "option_a": "LexException - Invalid character",
            "option_b": "ParseException - Syntax error",
            "option_c": "SemanticAnalysisException - Type error",
            "option_d": "ExecutionException - Runtime error (division by zero)",
            "option_e": "No exception (executes successfully)",
            "correct_answer": "D",
            "explanation": f"This code throws an ExecutionException because {reason}. The executor (Phase 4) runs the program and detects runtime errors like division by zero.",
            "difficulty": "hard"
        }
        return question

    def generate_good_execution_question(self, filename: str, code: str) -> Dict:
        """Generate question for successful execution test"""
        # Try to predict output (simplified - would need actual execution)
        output = "program output"
        if "print" in code:
            # Extract print statements
            import re
            prints = re.findall(r'print\s+"([^"]+)"', code)
            if prints:
                output = ''.join(prints)

        question = {
            "category": "executor",
            "subcategory": "goodexecution",
            "source_file": filename,
            "question_text": f"What is the output of this SPLAT program?",
            "code": code.strip(),
            "option_a": "Throws LexException",
            "option_b": "Throws ParseException",
            "option_c": "Throws SemanticAnalysisException",
            "option_d": "Throws ExecutionException",
            "option_e": f"Executes successfully (output: {output})",
            "correct_answer": "E",
            "explanation": f"This code executes successfully. It passes all four compiler phases (Lexer, Parser, Semantic Analyzer, Executor) and produces output.",
            "difficulty": "medium"
        }
        return question

    def analyze_all_tests(self) -> List[Dict]:
        """Analyze all SPLAT test files and generate questions"""
        questions = []

        for filepath in self.tests_dir.glob("*.splat"):
            filename = filepath.name
            code = self.read_file(filepath)

            if not code:
                continue

            exception_type, category = self.get_exception_type(filename)

            if "badlex" in filename:
                question = self.generate_lex_question(filename, code)
            elif "badparse" in filename:
                question = self.generate_parse_question(filename, code)
            elif "badsemantics" in filename:
                question = self.generate_semantic_question(filename, code)
            elif "badexecution" in filename:
                question = self.generate_execution_question(filename, code)
            elif "goodexecution" in filename:
                question = self.generate_good_execution_question(filename, code)
            else:
                continue

            questions.append(question)

        return questions

    def save_questions(self, output_file: str):
        """Save generated questions to JSON file"""
        questions = self.analyze_all_tests()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        print(f"Generated {len(questions)} questions from SPLAT tests")
        print(f"Saved to {output_file}")


if __name__ == "__main__":
    # Test the analyzer
    tests_dir = "../../data/splat_tests"
    output_file = "../questions/splat_tests.json"

    analyzer = SplatTestAnalyzer(tests_dir)
    analyzer.save_questions(output_file)
