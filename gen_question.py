import os
import pandas as pd
from google import genai
from google.genai import types
from typing import List, Dict, Union
import json
from datetime import datetime
import re

# Configure Gemini Pro API
client = genai.Client(api_key=GOOGLE_API_KEY)

def read_csv_files(*paths: str) -> List[pd.DataFrame]:
    """Read CSV files from multiple paths (directories or files).
    
    Args:
        *paths: Variable number of paths (can be directories or direct file paths)
    
    Returns:
        List of pandas DataFrames
    """
    dataframes = []
    
    for path in paths:
        try:
            df = pd.read_csv(path)
            dataframes.append(df)
            print(f"Successfully read file: {path}")
        except Exception as e:
            print(f"Error reading file {path}: {str(e)}")
    
    return dataframes

def extract_json_from_text(text: str) -> Dict:
    """Extract JSON from text response."""
    try:
        # Try to find JSON pattern in the text
        json_pattern = r'\{[\s\S]*\}'
        match = re.search(json_pattern, text)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except Exception as e:
        print(f"Error extracting JSON: {str(e)}")
    
    # If no valid JSON found, create empty structure
    return {
        'level1_qa': [],
        'level2_qa': [],
        'level3_qa': [],
        'level4_qa': []
    }

def save_to_csv(qa_pairs: Dict[str, List[Dict]], output_dir: str = "generated_questions"):
    """Save questions and answers to a CSV file.
    
    Args:
        qa_pairs: Dictionary containing question-answer pairs
        output_dir: Directory to save the CSV file
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create a list to store all rows
        rows = []
        
        # Process each level
        level_names = {
            'level1_qa': 'Cấp độ 1 - Câu hỏi cơ bản',
            'level2_qa': 'Cấp độ 2 - Câu hỏi cần ngữ cảnh',
            'level3_qa': 'Cấp độ 3 - Câu hỏi cần phân tích phức tạp',
            'level4_qa': 'Cấp độ 4 - Câu hỏi nhạy cảm với thời gian'
        }
        
        for level_key, level_name in level_names.items():
            if level_key in qa_pairs and isinstance(qa_pairs[level_key], list):
                for qa in qa_pairs[level_key]:
                    if isinstance(qa, dict) and 'question' in qa and 'answer' in qa:
                        rows.append({
                            'question': qa['question'],
                            'answer': qa['answer'],
                            'level': level_name
                        })
        
        if not rows:
            print("Không có dữ liệu để lưu vào CSV!")
            return
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(rows)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'qa_pairs_{timestamp}.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nĐã lưu {len(rows)} câu hỏi và câu trả lời vào file: {output_file}")
        
    except Exception as e:
        print(f"Lỗi khi lưu file CSV: {str(e)}")

def generate_questions(dataframes: List[pd.DataFrame]) -> Dict[str, List[Dict]]:
    """Generate questions and answers at different complexity levels using Gemini Pro."""
    # Prepare context from dataframes
    context = ""
    for i, df in enumerate(dataframes):
        context += f"\nDataFrame {i+1}:\n"
        context += f"Columns: {', '.join(df.columns)}\n"
        context += f"Sample data:\n{df.head().to_string()}\n"
    
    prompt = f"""Dựa trên dữ liệu CSV sau:
{context}

Hãy tạo 5 câu hỏi và câu trả lời cho mỗi loại sau (tất cả bằng tiếng Việt):

1. Câu hỏi có thể trả lời bằng LLM (câu hỏi cơ bản về sự kiện)
2. Câu hỏi có thể trả lời tốt hơn khi kết hợp LLM với tài liệu liên quan (cần thêm ngữ cảnh)
3. Câu hỏi chỉ có thể trả lời thông qua việc phân tích dữ liệu (cần phân tích phức tạp)
4. Câu hỏi nhạy cảm với thời gian (câu hỏi phụ thuộc vào thời điểm)

Bạn phải trả về đúng định dạng JSON sau:
{{
    "level1_qa": [
        {{"question": "Câu hỏi 1?", "answer": "Câu trả lời 1"}},
        {{"question": "Câu hỏi 2?", "answer": "Câu trả lời 2"}},
        {{"question": "Câu hỏi 3?", "answer": "Câu trả lời 3"}},
        {{"question": "Câu hỏi 4?", "answer": "Câu trả lời 4"}},
        {{"question": "Câu hỏi 5?", "answer": "Câu trả lời 5"}}
    ],
    "level2_qa": [
        {{"question": "Câu hỏi 1?", "answer": "Câu trả lời 1"}},
        {{"question": "Câu hỏi 2?", "answer": "Câu trả lời 2"}},
        {{"question": "Câu hỏi 3?", "answer": "Câu trả lời 3"}},
        {{"question": "Câu hỏi 4?", "answer": "Câu trả lời 4"}},
        {{"question": "Câu hỏi 5?", "answer": "Câu trả lời 5"}}
    ],
    "level3_qa": [
        {{"question": "Câu hỏi 1?", "answer": "Câu trả lời 1"}},
        {{"question": "Câu hỏi 2?", "answer": "Câu trả lời 2"}},
        {{"question": "Câu hỏi 3?", "answer": "Câu trả lời 3"}},
        {{"question": "Câu hỏi 4?", "answer": "Câu trả lời 4"}},
        {{"question": "Câu hỏi 5?", "answer": "Câu trả lời 5"}}
    ],
    "level4_qa": [
        {{"question": "Câu hỏi 1?", "answer": "Câu trả lời 1"}},
        {{"question": "Câu hỏi 2?", "answer": "Câu trả lời 2"}},
        {{"question": "Câu hỏi 3?", "answer": "Câu trả lời 3"}},
        {{"question": "Câu hỏi 4?", "answer": "Câu trả lời 4"}},
        {{"question": "Câu hỏi 5?", "answer": "Câu trả lời 5"}}
    ]
}}

Lưu ý: Chỉ trả về JSON, không thêm text khác."""

    response = client.models.generate_content(
        model="gemini-2.5-pro-exp-03-25",
        config=types.GenerateContentConfig(
            system_instruction="Bạn là một chuyên gia phân tích dữ liệu. Hãy tạo các câu hỏi và câu trả lời phù hợp dựa trên dữ liệu CSV được cung cấp. Tất cả câu hỏi và câu trả lời phải bằng tiếng Việt. Bạn PHẢI trả về JSON hợp lệ theo đúng format đã cho."
        ),
        contents=prompt
    )
    
    try:
        # Print raw response for debugging
        print("\nRaw response from Gemini:")
        print(response.text)
        
        # Try to extract JSON from response
        qa_pairs = extract_json_from_text(response.text)
        
        # Validate the structure of qa_pairs
        required_keys = ['level1_qa', 'level2_qa', 'level3_qa', 'level4_qa']
        for key in required_keys:
            if key not in qa_pairs:
                print(f"Warning: Missing key '{key}' in response")
                qa_pairs[key] = []
            elif not isinstance(qa_pairs[key], list):
                print(f"Warning: '{key}' is not a list")
                qa_pairs[key] = []
        
        return qa_pairs
    except Exception as e:
        print(f"Error processing response: {str(e)}")
        print("Raw response:")
        print(response.text)
        return {
            'level1_qa': [],
            'level2_qa': [],
            'level3_qa': [],
            'level4_qa': []
        }

def main():
    # Read CSV files from multiple paths
    dataframes = read_csv_files(
        r'D:\scraping\crawl_results_20250509_101615\khcn.csv'
    )
    
    if not dataframes:
        print("No CSV files found in the specified paths.")
        return
    
    # Generate questions and answers
    qa_pairs = generate_questions(dataframes)
    
    # Print results
    print("\nCác câu hỏi và câu trả lời được tạo:")
    
    print("\nCấp độ 1 - Câu hỏi cơ bản:")
    for qa in qa_pairs.get('level1_qa', []):
        print(f"\nCâu hỏi: {qa['question']}")
        print(f"Câu trả lời: {qa['answer']}")
    
    print("\nCấp độ 2 - Câu hỏi cần ngữ cảnh:")
    for qa in qa_pairs.get('level2_qa', []):
        print(f"\nCâu hỏi: {qa['question']}")
        print(f"Câu trả lời: {qa['answer']}")
    
    print("\nCấp độ 3 - Câu hỏi cần phân tích phức tạp:")
    for qa in qa_pairs.get('level3_qa', []):
        print(f"\nCâu hỏi: {qa['question']}")
        print(f"Câu trả lời: {qa['answer']}")
    
    print("\nCấp độ 4 - Câu hỏi nhạy cảm với thời gian:")
    for qa in qa_pairs.get('level4_qa', []):
        print(f"\nCâu hỏi: {qa['question']}")
        print(f"Câu trả lời: {qa['answer']}")
    
    # Save to CSV
    save_to_csv(qa_pairs)

if __name__ == "__main__":
    main()
