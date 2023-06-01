import streamlit as st
import pyfolio as py
from streamlit_pages.home import render_home
from streamlit_pages.about import render_about

# turn off warning signs for cleaner code
from warnings import filterwarnings
filterwarnings("ignore")

st.set_page_config(page_title="Portfolio Optimizer")

# Function to render the navigation menu
def render_navigation_menu():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ("Home", "About"))

    # Call the respective page function based on the user's selection
    if selection == "Home":
        render_home()
    elif selection == "About":
        render_about()

# Main function to run the application
def main():
    st.title("Portfolio Optimization Center")
    render_navigation_menu()

# Run the application
if __name__ == "__main__":
    main()