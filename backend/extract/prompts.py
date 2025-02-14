PROMPTS = {
    "zero-shot": """What airline is mentioned in this tweet? Only respond with the official airline name, not an abbreviation or variation on the name. If there is no airline name, return "No airline found".

Tweet: '{tweet}'""",

    "one-shot": """Extract the official airline name from the tweet. If there is no airline name, return "No airline found". Use the example format below:

Tweet: '@AmericanAir your service is terrible!'
Airlines: American Airlines

Tweet: '{tweet}'
Airlines:""",

    "few-shot": """Extract the official airline names from the tweet. If there is no airline name, return "No airline found". Use the examples format below:

Tweet: '@AmericanAir your service is terrible!'
Airlines: American Airlines

Tweet: '@United to LAX then @SouthwestAir to Vegas'
Airlines: United Airlines, Southwest Airlines

Tweet: '@USAirways and @JetBlue both lost my bags today'
Airlines: US Airways, JetBlue Airways

Tweet: '@VirginAmerica best airline ever'
Airlines: Virgin America

Tweet: '{tweet}'
Airlines:"""
}