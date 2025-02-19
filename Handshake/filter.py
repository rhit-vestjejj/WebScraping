import pandas as pd

# Load the CSV file
file_path = "simplify_jobs.csv"  # Update with your actual file path
df = pd.read_csv(file_path)

# Define the target locations
target_locations = ["MO", "IL", "IN"]

# Function to extract city and state
def extract_city_state(place):
    if isinstance(place, str):
        parts = place.split(", ")
        if len(parts) >= 2:
            return parts[-2]
    return None

# Function to check if a job is within 25 miles
def is_nearby(place):
    if(place == "Remote in USA"):
        return True
    city_state = extract_city_state(place)
    print(city_state)
    if city_state in target_locations:
        return True
    return False

def filter_main():
    # Create an empty list to store rows that match the filter
    filtered_rows = []

    # Iterate through each row instead of using .apply()
    for index, row in df.iterrows():
        place = row["Place"]
        print(f'{place} + {index}')
        if is_nearby(place):
            filtered_rows.append(row)

    # Convert the list back to a DataFrame
    filtered_df = pd.DataFrame(filtered_rows)

    # Save the filtered data
    filtered_file_path = "filtered_jobs.csv"
    filtered_df.to_csv(filtered_file_path, index=False)

    print(f"Filtered jobs saved to {filtered_file_path}")

filter_main()