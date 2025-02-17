Hello Team,

Thanks so much for the opportunity to work on the air travel sentiment analysis project. I really enjoyed our time in Seattle at your office. As we discussed, you are developing a new product offering that lets users view airline ratings based on customer sentiment. As a frequent traveler I think this will be a really helpful rating system that will differentiate you from other travel sites. I know your goal is to increase customer engagement by 10%, site visit duration by 30 seconds, and new customer acquisition by 20%. We are excited to support this effort, and believe that the OpenAI API will be a great fit for this project.

Based on our discussion and discovery session on 15th January, I have prepared a proof of concept for the Airline Name Tweet Extractor. This is one small part of the project, and does not include the use of the X (formerly Twitter) API, specific sentiment analysis, or integration with your end user applications. We will get to that next once we validate the approach and you all have a chance to see the API in action and share feedback.

Project Overview:
The project that I'm sharing is a command line tool that allows you to see what can be accomplished with the OpenAI API and a static dataset. For this example I have used a dataset from Kaggle that is publicly available on Kaggle.

Methodology:
The tool loops through each tweet in the dataset and extracts the airline names using 5 different approaches:

1. Zero-shot prompt engineering: a simple and concise prompt that uses the model's own capabilities to extract the airline names without any examples
2. One-shot prompt engineering: an example-based prompt that uses a single example to extract the airline names
3. Few-shot prompt engineering: a prompt that uses multiple examples to extract the airline names
4. Embeddings-based extraction: a method that uses the OpenAI API to generate embeddings for the tweet and the airline names, and then uses cosine similarity to find the most similar airline name
5. Fine-tuned model extraction: a method that uses a custom-trained model to extract the airline names

The reason we implement these different methods is to show the flexibility of the OpenAI API and the different ways to approach the problem. There are tradeoffs to each method. For example, zero-shot prompt engineering is often the fastest and most efficient method. It will return a result quickly, and uses fewer tokens, reducing the cost of the API call. But it is usually not as accurate as the other methods, especially for more specialized tasks like this one. On the other hand, the fine-tuned model extraction method is the most accurate, but it is also the slowest and most expensive method, requiring a lot of data and compute resources to train the model.

Our overall goal in designing your solution is to identify the method that balances the tradeoffs between cost, speed, and accuracy. Based on our discovery session, we will be placing a high priority on accuracy, since your customers will be relying on accurate identification of airline names to make decisions about which airline to fly.

The repository includes a tool called `analyze_results.sh` that allows you to analyze the accuracy, speed, and cost of the different methods. It also uses zero-shot prompt engineering to recommend improvements to the prompt used in the method.

How to use the tool:

Detailed instructions can be found in the README.md file. Read on for a quick start guide. For a brief video-based walkthrough of the tool, please see the video here: https://www.loom.com/share/2e9196cdc6b445ad800a436456586a0f?sid=9f7289a4-7504-4772-aa01-6589f3cb2b0b

Prerequisites:

- Python 3.10 or higher
- OpenAI API key
- Linux or MacOS operating system (this has been tested on Ubuntu 22.04 and MacOS 14.4)

1. Clone or unzip the repository

```
git clone https://github.com/yourusername/airline-tweet-extractor.git
```

2. Run the setup script

```
./setup.sh
```

This will install the dependencies and set up the environment. As long as you have the prerequisites installed, you should be able to run all setup scripts successfully. The setup script will also prompt you to enter your OpenAI API key, which will be saved in the `.env` file. The repository includes a `.env.example` file that shows the required variables and is set to ignore the `.env` file by default.

3. Run the extraction script

```
./run_extraction.sh
```

This will give you the ability to select a dataset, and your method of choice. It also gives you the option to write a single tweet prompt and verify the results for test. You will be able to see the accuracy, cost, and time taken for each method and run comparison across all methods. The command line tool will prompt you to:

1. Select a dataset
2. Select a method
3. Optional: Write a single tweet prompt and verify the results for test
4. Optional: Run comparison across all methods
5. See the accuracy, cost, and time taken for each method
6. See the comparison summary

Each run of the tool will create a detailed log file in the `logs` directory. This log file will include the accuracy, cost, and time taken for each method, as well as the comparison summary. It will also write an output file in the `output` directory with the results for each method.

Recommendations:

Use the fine-tuned model to extract the airline names. It is the most accurate method, and accuracy is a top priority based on feedback from your product team, trust and safety team, and the sample of customers we spoke with. This was also one of the most cost-effective methods, and the second most time-efficient method. Fine-tuning the model can take 30 minutes to many hours, depending on the size of the dataset. This does incur additional cost and developer time, but this finetuning does not need to be run with high frequency, and can be automated to run periodically. Since you know the airlines that you are interested in, you can maintain a list of airlines and their corresponding embeddings. This makes the use-case a strong candidate for a fine-tuned model, since it will be able to achieve a high accuracy and the model can be retrained as new airlines are added. We can also assist in implementing canary evaluations to evaluate model performance and alert you if accuracy falls below a threshold so that you can retrain the model.

As a next step I recommend that we use the same repository and approach to compare methods for sentiment analysis. We have seen a lot of customer success with sentiment analysis, and it is a great use-case for the OpenAI API. Once we have identified an overall method for airline identification and sentiment analysis that achieves your required balance over accuracy, speed, and cost, we can integrate with your existing applications and infrastructure.

Next Steps:

1. Please give this repository a try. Feel free to make changes to the code and the prompt to see how it performs with different methods.
2. I encourage you to try the different methods and see which one performs best for your use-case, and evaluate the tradeoffs between accuracy, speed, and cost.
3. I have sent a calendar invite for a follow-up call to review the results and share feedback 2 weeks from today at our usual time. Please suggest a new time if there is a better one.
4. Share your questions, feedback, ideas, and concerns with me via email in the meantime. If anything is unclear I want to address it right away. I will make time.
5. In our meeting next week I would like to review the development timeline and schedule a date to demo the full proof of concept to your executive team.

Thank you so much. It's been really great working with you. I look forward to seeing what you all build to help travelers the airline experience they're looking for.

Sam
