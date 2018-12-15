default_init_steps = {
    "load": None,
    "store_map": None,
    "init": None,
}

service_steps = {
    "Delivery Service": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Pop. density", "Homeownership rate", "Median rent"],
        "fit": None,
        "plots": None
    },
    "Assemble Furniture": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "stepwise": None,
        "fit": None  # Fit linear regression model
    },
    "Electrical Work": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Percent. foreign born', 'Unemployment rate'],
        "fit": None  # Fit linear regression model
    },
    "Plumbing": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Percent. foreign born', 'Highschool'],
        "fit": None  # Fit linear regression model
    },
    "Bartending": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Homeownership rate', 'Per. white'],
        "fit": None  # Fit linear regression model
    },
    "General Cleaning": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Percent. foreign born', 'Unemployment rate', 'Median rent'],
        "fit": None  # Fit linear regression model
    },
    "General Handyman": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Per. white'],
        "fit": None  # Fit linear regression model
    },
    "Heavy Lifting": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Homeownership rate', 'Pop. density', 'Unemployment rate'],
        "fit": None  # Fit linear regression model
    },
    "Help Cooking & Serving Food": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Homeownership rate', 'Percent. foreign born', 'Median rent'],
        "fit": None  # Fit linear regression model
    },
    "Painting": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Unemployment rate'],
        "fit": None  # Fit linear regression model
    },
    "Personal Assistant": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Homeownership rate', 'Percent. foreign born', 'Median rent'],
        "fit": None  # Fit linear regression model
    },
    "Yard Work & Removal": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ['Homeownership rate', 'Percent. foreign born', 'Median rent'],
        "fit": None  # Fit linear regression model
    }
}

'''plumbing, electrical, assemble furn, bartending, handyman, heavy lifting, painting, personal, yard work
"vif": {  # Calculate VIF and remove variables over threshold of 10
    "threshold": 10,
    "keep": ['Unemployment rate'] #Sentiment here is good
},
'''
'''
        "leave": ['Pop. density', 'Homeownership rate', 'Median household income'],
        "scale": None,  # Scale/standardise
        "fit": None  # Fit linear regression model
        
        "leave": ['Homeownership rate', 'Percent. foreign born'],
        "scale": None,
        "fit": None
'''