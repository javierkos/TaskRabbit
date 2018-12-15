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
        "leave": ["Highschool", "Per. white", "Homeownership rate"],
        "fit": None,
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
        "leave": ["Highschool", "Per. white", "Homeownership rate"],
        "fit": None  # Fit linear regression model
    },
    "Plumbing": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Highschool", "Per. white", "Homeownership rate"],
        "fit": None,  # Fit linear regression model
        "plots": None
    },
    "Bartending": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Pop. density", "Highschool", "Homeownership rate"],
        "fit": None  # Fit linear regression model
    },
    "General Cleaning": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Median rent", "Crime rate", "Percent. below poverty"],
        "fit": None  # Fit linear regression model
    },
    "General Handyman": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Percent. below poverty", "Highschool", "Homeownership rate", "Per. white", "Median rent"],
        "fit": None  # Fit linear regression model
    },
    "Heavy Lifting": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Homeownership rate", "Unemployment rate"],
        "fit": None  # Fit linear regression model
    },
    "Help Cooking & Serving Food": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Per. white", "Highschool"],
        "fit": None  # Fit linear regression model
    },
    "Painting": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Homeownership rate"],
        "fit": None,  # Fit linear regression model,
    },
    "Personal Assistant": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": [],
        "fit": None  # Fit linear regression model
    },
    "Yard Work & Removal": {
        "scale": "standard",
        "vif": {
            "threshold": 10
        },
        "leave": ["Homeownership rate", "Highschool", "Percent. below poverty", "Per. white"],
        "fit": None  # Fit linear regression model
    }
}