import streamlit as st
import pickle
import pandas as pd

# Set page title
st.set_page_config(page_title="Recommend Apartments")

# Load the datasets
location_df = pickle.load(open("dataset/location_distance.pkl", "rb"))
cosine_sim1 = pickle.load(open("dataset/cosine_sim1.pkl", "rb"))
cosine_sim2 = pickle.load(open("dataset/cosine_sim2.pkl", "rb"))
cosine_sim3 = pickle.load(open("dataset/cosine_sim3.pkl", "rb"))


# Define the recommendation function
def recommend_properties_with_scores(property_name, top_n=5):
    # Calculate the weighted cosine similarity matrix
    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3

    # Get the similarity scores for the property using its name as the index
    sim_scores = list(
        enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)])
    )

    # Sort properties based on the similarity scores
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices and scores of the top_n most similar properties
    top_indices = [i[0] for i in sorted_scores[1 : top_n + 1]]
    top_scores = [i[1] for i in sorted_scores[1 : top_n + 1]]

    # Retrieve the names of the top properties using the indices
    top_properties = location_df.index[top_indices].tolist()

    # Create a dataframe with the results
    recommendations_df = pd.DataFrame(
        {"PropertyName": top_properties, "SimilarityScore": top_scores}
    )

    return recommendations_df


# Title
st.title("Select Location and Radius")

# Select location
selected_location = st.selectbox("Location", sorted(location_df.columns.to_list()))

# Enter radius
radius = st.number_input("Radius in Kms")

# Button to search apartments
if st.button("Search"):
    # Get apartments within the radius
    result_ser = location_df[location_df[selected_location] < radius * 1000][
        selected_location
    ].sort_values()

    # Store the search results in session state to persist the data
    st.session_state["apartments"] = [
        str(key) + "--> " + str(value) for key, value in result_ser.items()
    ]

# Display the radio button for apartment selection if apartments data is available
if "apartments" in st.session_state and st.session_state["apartments"]:
    selected_apartment = st.radio(
        "Select Apartment for recommendations", st.session_state["apartments"]
    )

    # If an apartment is selected, display the recommendations
    if selected_apartment:
        st.subheader("Some recommendations")
        apartment_name = selected_apartment.split("-->")[
            0
        ]  # Extract the apartment name
        df = recommend_properties_with_scores(apartment_name)
        st.dataframe(df)
