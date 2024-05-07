# Real-time Google Research Assistant

This Streamlit application acts as a real-time research assistant, leveraging the power of Google search and Groq models to generate responses to user queries based on content scraped from the first 10 pages of Google search results.

## Features

- **Search and Scrape:** Automates the process of searching Google with a user's query, scraping the first 10 pages of results.
- **In-Memory Vector Database:** Uses the scraped content to create an in-memory vector database for efficient information retrieval.

## Installation

### Dependencies

Before running the application, you need to install the necessary dependencies. Please follow the steps below:

1. **Create a Conda Environment (Optional but Recommended):**
2. **Install Required Python Packages:**
3. **Install Playwright:**

### Setting Up Your API Key

- An Groq API key is necessary for running the application. You can get your API key from [Groq Platform](https://console.groq.com/keys) if you have a Groq account.

## Usage

1. **Start the Streamlit Application:**
Run the application by navigating to the application's directory and using the command:

2. **Enter Your Groq API Key:**
Upon launching the application, you'll be prompted to enter your Groq API key in the sidebar.

3. **Using the Application:**
- Enter your research question in the provided text input.
- Click the "Search" button to initiate the research process.
- Wait for the application to scrape Google search results, analyze the content, and generate a response based on the most relevant information.

## Limitations and Notes

- The application requires a stable internet connection for scraping and accessing the OpenAI API.
- Response times may vary based on the complexity of the query and the volume of content to be analyzed.
- The application does not store user queries or responses, ensuring privacy.

## Contributions

Contributions to improve the Real-time Google Research Assistant are welcome. Please feel free to fork the repository, make changes, and submit pull requests.

## Suppport Us

<a href="https://www.buymeacoffee.com/blazzmocompany"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=blazzmocompany&button_colour=40DCA5&font_colour=ffffff&font_family=Cookie&outline_colour=000000&coffee_colour=FFDD00"></a>


[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/blazzmocompany)

## License

This project is open-sourced under the MIT License. See the [LICENSE](./LICENSE) file for more details.
