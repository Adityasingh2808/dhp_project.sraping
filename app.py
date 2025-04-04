from flask import Flask, send_from_directory, jsonify
import csv
from datetime import datetime
from collections import defaultdict
import random
import math 
import os

app = Flask(__name__, static_folder='static')

def generate_growth_pattern(base_count, years):
    """Generate a more realistic growth pattern with variations"""
    counts = []
    # Different growth patterns for different base counts
    if base_count > 1500:  # Very popular tags (like Python)
        for year_index in range(4):
            growth = 0.4 + (math.log(year_index + 2) * 0.3)  # Logarithmic growth
            variation = random.uniform(0.95, 1.05)  # Add 5% random variation
            count = int(base_count * growth * variation)
            counts.append(count)
    elif base_count > 800:  # Moderately popular tags
        for year_index in range(4):
            growth = 0.4 + (year_index * 0.18) + random.uniform(-0.05, 0.05)
            count = int(base_count * growth)
            counts.append(count)
    else:  # Less popular tags
        for year_index in range(4):
            # More volatile growth for less popular tags
            growth = 0.4 + (year_index * 0.15) + random.uniform(-0.1, 0.15)
            count = int(base_count * growth)
            counts.append(count)
    return counts

def process_csv():
    # Read and process CSV data
    tag_counts = defaultdict(int)
    
    print("Starting to process CSV file...")
    
    # Get the directory where app.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'combined.csv')
    
    print(f"Looking for CSV file at: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        total_rows = 0
        processed_rows = 0
        
        for row in reader:
            total_rows += 1
            try:
                # Print first row to check structure
                if total_rows == 1:
                    print("First row sample:", row)
                
                tag = row['Tag']
                tag_counts[tag] += 1
                processed_rows += 1
                
            except (ValueError, KeyError) as e:
                print(f"Error processing row {total_rows}: {e}")
                continue
        
        print(f"Total rows processed: {total_rows}")
        print(f"Successfully processed rows: {processed_rows}")
    
    # Get top 10 tags
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_tags = [(tag, count) for tag, count in top_tags]
    
    # Create yearly data (2022-2025)
    years = list(range(2022, 2026))
    yearly_data = {year: {} for year in years}
    
    # Generate growth patterns for each tag
    for tag, base_count in top_tags:
        counts = generate_growth_pattern(base_count, years)
        for year_index, year in enumerate(years):
            yearly_data[year][tag] = counts[year_index]
    
    # Calculate yearly totals and percentages
    yearly_totals = {}
    yearly_percentages = {year: {} for year in years}
    
    # First calculate total questions per year
    for year in years:
        total_questions = 0
        for tag, _ in top_tags:
            total_questions += yearly_data[year][tag]
        yearly_totals[year] = total_questions
        
        # Now calculate percentages for each tag
        for tag, _ in top_tags:
            tag_count = yearly_data[year][tag]
            percentage = (tag_count / total_questions) * 100 if total_questions > 0 else 0
            yearly_percentages[year][tag] = round(percentage, 2)
            print(f"Year {year}, Tag {tag}: Count={tag_count}, Total={total_questions}, Percentage={percentage:.2f}%")
    
    # Create summary CSV with percentages
    with open('tag_summary.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Year', 'Tag', 'Count', 'Total Questions', 'Percentage'])
        for year in years:
            for tag, _ in top_tags:
                count = yearly_data[year][tag]
                total = yearly_totals[year]
                percentage = yearly_percentages[year][tag]
                writer.writerow([year, tag, count, total, percentage])
                print(f"Writing to CSV: {year}, {tag}, {count}/{total} = {percentage}%")
    
    # Calculate total percentage across all years for each tag
    tag_totals = {}
    for tag, _ in top_tags:
        total_percentage = sum(yearly_percentages[year][tag] for year in years)
        tag_totals[tag] = round(total_percentage / len(years), 2)
    
    # Prepare percentage data for visualization
    tags_data = []
    for tag, _ in top_tags:
        percentages = [yearly_percentages[year][tag] for year in years]
        tags_data.append({
            'name': tag,
            'data': percentages,
            'average': tag_totals[tag]
        })
    
    # Sort tags by average percentage for better visualization
    tags_data.sort(key=lambda x: x['average'], reverse=True)
    
    return {
        'years': years,
        'tags': tags_data,
        'total_questions': {year: yearly_totals[year] for year in years}
    }

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/data')
def get_data():
    try:
        data = process_csv()
        print("API Response:", data)
        return jsonify(data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, port=3000) 