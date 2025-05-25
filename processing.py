import os
import pandas as pd
import glob

def process_crawled_files(directory_path):
    # Get all content_*.txt files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "content_*.txt"))
    
    # Create lists to store data
    ids = []
    contents = []
    categories = []
    
    # Process each file
    for file_path in txt_files:
        try:
            # Get file number from filename (content_1.txt -> 1)
            file_name = os.path.basename(file_path)
            file_id = int(file_name.replace('content_', '').replace('.txt', ''))
            
            # Read content from file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Add data to lists
            ids.append(file_id)
            contents.append(content)
            categories.append("uet, chương trình đào tạo trí tuệ nhân tạo")
            
            print(f"Processed file: {file_name}")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame({
        'id': ids,
        'category': categories,
        'content': contents,
    })
    
    # Sort by id
    df = df.sort_values('id')
    
    # Save to CSV
    output_file = os.path.join(directory_path, 'processed_data.csv')
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\nProcessing completed. Results saved to: {output_file}")
    print(f"Total files processed: {len(txt_files)}")
    return output_file

if __name__ == "__main__":
    # Directory containing crawled files
    directory_path = r"D:\scraping\crawl_results_20250511_090658"
    
    # Process files
    process_crawled_files(directory_path)
