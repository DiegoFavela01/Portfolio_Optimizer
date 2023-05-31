import streamlit as st
from streamlit_pages.home import render_home
from streamlit_pages.files import render_files
from streamlit_pages.about import render_about

# Function to render the navigation menu
def render_navigation_menu():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ("Home", "Files", "About"))

    # Call the respective page function based on the user's selection
    if selection == "Home":
        render_home()
    elif selection == "Files":
        render_files()
    elif selection == "About":
        render_about()

# Main function to run the application
def main():
    st.title("Portfolio Optimization Center")
    render_navigation_menu()

# Run the application
if __name__ == "__main__":
    main()