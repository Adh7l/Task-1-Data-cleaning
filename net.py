import pandas as pd
import numpy as np
from pathlib import Path

# ---------- CONFIG ----------
INPUT_FILENAME = "netflix_titles.csv"   # put this in same folder as script, or give full path
OUTPUT_FILENAME = "netflix_cleaned.csv"
SUMMARY_FILENAME = "cleaning_summary.txt"
# ----------------------------

def load_df(path):
    print(f"Loading dataset from: {path}")
    # Using 'comment' helps ignore header lines if they start with '#' (though less common in CSV)
    df = pd.read_csv(path, low_memory=False)
    print("Loaded rows:", df.shape[0], "columns:", df.shape[1])
    return df

def basic_report(df):
    print("\n--- Basic info ---")
    # df.info() shows data types and non-null counts
    print(df.info(verbose=False, memory_usage="deep"))
    print("\nMissing values per column:")
    print(df.isnull().sum())

def drop_unnecessary_columns(df):
    # Commonly unwanted columns in exported datasets
    cols_to_drop = ['Unnamed: 0', 'index']
    
    # Identify which columns actually exist in the current DataFrame
    existing_cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    
    if existing_cols_to_drop:
        df = df.drop(columns=existing_cols_to_drop, errors='ignore')
        print(f"\nDropped unnecessary columns: {existing_cols_to_drop}")
        return df, f"Dropped unnecessary columns: {', '.join(existing_cols_to_drop)}"
    
    return df, "No unnecessary columns dropped."

def drop_duplicates(df):
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    removed_count = before - after
    print(f"\nDuplicates removed: {removed_count}")
    return df, f"Removed duplicate rows: {removed_count} rows."

def standardize_text_columns(df):
    # Columns expected on Netflix dataset that need text cleanup
    text_cols = ['type', 'title', 'director', 'cast', 'country', 'listed_in', 'rating', 'description']
    cleaned_count = 0

    for col in text_cols:
        if col in df.columns and df[col].dtype == 'object':
            # 1. Strip whitespace and convert to string (handles mixed types)
            df[col] = df[col].astype(str).str.strip()
            
            # 2. Convert standard missing string representations to np.nan
            # This is more efficient than the previous dictionary replace
            df[col] = df[col].replace(['nan', 'none', ''], np.nan, regex=False)
            cleaned_count += 1
            
    print(f"\nStandardized {cleaned_count} text columns (trim + null normalization).")
    return df, f"Standardized {cleaned_count} text columns (trimmed whitespace, normalized missings)."

def handle_missing_values(df):
    notes = []
    
    # 1. Fill missing text columns with 'Not Available' or similar
    fill_na_cols = {'director': 'Not Available', 'cast': 'Not Available', 'country': 'Not Available'}
    for col, value in fill_na_cols.items():
        if col in df.columns:
            df[col] = df[col].fillna(value)
            notes.append(f"Replaced missing {col} with '{value}'.")
            
    if 'rating' in df.columns:
        df['rating'] = df['rating'].fillna("Not Rated")
        notes.append("Replaced missing rating with 'Not Rated'.")
        
    # 2. Handle 'release_year' (numeric)
    if 'release_year' in df.columns:
        # Coerce any bad values into NaN
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
        if df['release_year'].isnull().any():
            median_year = int(df['release_year'].median(skipna=True))
            df['release_year'] = df['release_year'].fillna(median_year).astype(int)
            notes.append(f"Filled missing release_year with median: {median_year}")
        else:
            # Ensure it is integer type if no missings were present
            df['release_year'] = df['release_year'].astype(int)
            
    print("\nHandled missing values for key columns.")
    return df, notes

def fix_duration_column(df):
    notes = []
    if 'duration' in df.columns:
        # Fill missings before splitting to avoid error on split
        df['duration'] = df['duration'].fillna("0 min") 
        
        # Split '93 min' or '1 Season' into two parts
        split_duration = df['duration'].str.split(' ', expand=True)
        
        # Create new columns: duration_value (numeric) and duration_unit (text)
        # pd.to_numeric converts the first part, errors='coerce' turns non-numbers (like text) into NaN
        df['duration_value'] = pd.to_numeric(split_duration[0], errors='coerce').fillna(0).astype(int)
        df['duration_unit'] = split_duration[1].str.lower()
        
        # Drop the original column as it is now split
        df = df.drop(columns=['duration'])
        
        notes.append("Cleaned 'duration' by splitting it into 'duration_value' (int) and 'duration_unit'.")
        print("\nCleaned duration into duration_value (int) and duration_unit.")
    return df, notes

def fix_date_added(df):
    notes = []
    if 'date_added' in df.columns:
        # Robustly parse the date string (e.g., "September 9, 2019")
        df['date_added_parsed'] = pd.to_datetime(df['date_added'], errors='coerce', infer_datetime_format=True)
        null_count = df['date_added_parsed'].isnull().sum()
        
        # Create a clean format for direct use
        df['date_added_ddmmyyyy'] = df['date_added_parsed'].dt.strftime('%d-%m-%Y')
        
        notes.append(f"Parsed 'date_added' into 'date_added_parsed' (datetime) and 'date_added_ddmmyyyy' (string). Failed to parse: {null_count} entries.")
        print(f"\nParsed date_added. Failed to parse: {null_count} entries (will remain NaT).")
    return df, notes

def rename_columns_snakecase(df):
    # Convert to lowercase, replace spaces with underscore, remove special characters
    new_cols = {c: c.strip().lower().replace(' ', '_').replace('.', '').replace('-', '') for c in df.columns}
    df = df.rename(columns=new_cols)
    print("\nRenamed columns to snake_case.")
    return df, "Converted all column names to snake_case."

def final_checks_and_export(df, out_path):
    print("\nFinal dataset shape:", df.shape)
    # write cleaned CSV
    df.to_csv(out_path, index=False)
    print(f"Cleaned dataset saved to: {out_path}")

def write_summary(path, original_shape, final_shape, notes):
    with open(path, 'w', encoding='utf-8') as f:
        f.write("Netflix dataset cleaning summary\n")
        f.write("===============================\n")
        f.write(f"Original shape: {original_shape[0]} rows, {original_shape[1]} cols\n")
        f.write(f"Final shape: {final_shape[0]} rows, {final_shape[1]} cols\n\n")
        f.write("Actions performed:\n")
        for n in notes:
            f.write("- " + n + "\n")
    print(f"Cleaning summary written to {path}")

def main():
    in_path = Path(INPUT_FILENAME)
    out_path = Path(OUTPUT_FILENAME)
    summary_path = Path(SUMMARY_FILENAME)
    notes = []
    
    if not in_path.exists():
        print(f"ERROR: Input file not found at {in_path.resolve()}")
        return

    df = load_df(in_path)
    original_shape = df.shape

    basic_report(df)
    
    # Cleaning steps
    df, note = drop_unnecessary_columns(df)
    notes.append(note)
    
    df, note = drop_duplicates(df)
    notes.append(note)
    
    df, note = standardize_text_columns(df)
    notes.append(note)
    
    df, missing_notes = handle_missing_values(df)
    notes.extend(missing_notes)
    
    df, duration_notes = fix_duration_column(df)
    notes.extend(duration_notes)
    
    df, date_notes = fix_date_added(df)
    notes.extend(date_notes)
    
    df, note = rename_columns_snakecase(df)
    notes.append(note)

    final_shape = df.shape
    final_checks_and_export(df, out_path)

    write_summary(summary_path, original_shape, final_shape, notes)

    # Print final confirmation lines for you to copy
    print("\n--- Completed ---")
    print(f"Final Rows & Columns: {final_shape}")
    print(f"Output file: {out_path.resolve()}")
    print(f"Summary file: {summary_path.resolve()}")

if __name__ == "__main__":
    main()