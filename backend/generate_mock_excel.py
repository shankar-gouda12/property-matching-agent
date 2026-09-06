import pandas as pd

# Creating a beautiful inventory matching standard requirements
data = {
    "Property Type": [
        "Apartment", "Apartment", "Villa", "Villa", "Plot", "Row House", "Penthouse", "Apartment"
    ],
    "BHK": [
        "3 BHK", "2 BHK", "4 BHK", "3 BHK", "Other", "4 BHK", "5 BHK", "3 bhk"
    ],
    "Budget (Cr)": [
        1.10, 0.75, 3.50, 1.95, 0.50, 2.20, 4.80, 1.25
    ],
    "Location": [
        "Hennur", "Thanisandra", "Devanahalli", "Yelahanka", "Hebbal", "Whitefield", "Sarjapur", "Hennur Road"
    ],
    "Status": [
        "Ready to Move", "Under Construction", "New Launch", "Ready to Move", "Completed", "Under Construction", "Ready to Move", "Ready to Move"
    ],
    "Project Name": [
        "Prestige Vista", "Sobha Dream Acres", "Embassy Boulevard", "Adarsh Wisteria", "Godrej Woods", "Assetz Marq", "Total Environment Windmills", "Purva Palm Beach"
    ],
    "Builder": [
        "Prestige Group", "Sobha Limited", "Embassy Group", "Adarsh Group", "Godrej Properties", "Assetz Group", "Total Environment", "Puravankara"
    ],
    "Area (SqFt)": [
        1650, 1200, 4200, 2800, 2400, 3100, 5500, 1800
    ],
    "Facing": [
        "East", "North", "East", "West", "South", "East", "East", "West"
    ],
    "Amenities": [
        "Gym, Pool, Club", "Gym, Play Area", "Private Pool, Gym", "Garden, Club", "None", "Pool, Security", "Club, Gym, Pool", "Pool, Gym, Tennis"
    ],
    "Possession": [
        "Immediate", "Dec 2027", "Immediate", "Immediate", "Immediate", "Jun 2028", "Immediate", "Immediate"
    ],
    "Contact": [
        "9876543210", "9876543211", "9876543212", "9876543213", "9876543214", "9876543215", "9876543216", "9876543217"
    ]
}

df = pd.DataFrame(data)
df.to_excel("data/Inventory.xlsx", index=False)
print("Mock Inventory.xlsx created successfully in data/Inventory.xlsx")
