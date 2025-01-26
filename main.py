import streamlit as st
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyCAOvmdRTfN9BCAWcACukXRItenG9t5sBA")
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to predict admission likelihood using Gemini API
def predict_admission(jamb_score, preferred_course, preferred_institution):
    prompt = f"""
    Predict the admission likelihood for the following student:
    JAMB score: {jamb_score}.
    Preferred Course: {preferred_course}.
    Preferred Institution: {preferred_institution}.
    Respond with: 'Highly likely', 'Likely', 'Unlikely', or 'Highly unlikely'.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# Function to generate recommended alternatives using Gemini API
def generate_recommendations(jamb_score, preferred_course, preferred_institution):
    prompt = f"""
    Based on the student's preferred course '{preferred_course}' and institution '{preferred_institution}',
   with a jamb score of '{jamb_score}', suggest four alternative universities and related courses that are good options for the student to study if his jamb score doesnt met the minimum requirements.
    Format the response as a list: University - Course.
    """
    try:
        response = model.generate_content(prompt)
        recommendations = response.text.strip().split("\n")
        return recommendations
    except Exception as e:
        return [f"Error: {e}"]

# Streamlit app
st.title("Welcome to Nigerian University Admission Predictor!")
st.subheader("Plan your future with confidence")
st.write("""
  This tool helps Nigerian students predict their chances of university admission.
""")

with st.sidebar:
    st.header("Enter Your Details")
    jamb_score = st.number_input("Enter your JAMB score:", min_value=0, max_value=400, value=200)
    preferred_course = st.text_input("Preferred Course:")
    preferred_institution = st.text_input("Preferred Institution:")

    # Check if all fields are filled before submission
    if st.button("Submit"):
        if jamb_score and preferred_course and preferred_institution:
            st.write("Processing your data...")
            prediction = predict_admission(jamb_score, preferred_course, preferred_institution)
            recommendations = generate_recommendations(jamb_score, preferred_course, preferred_institution)
            st.session_state["prediction"] = prediction
            st.session_state["recommendations"] = recommendations
        else:
            st.error("Please fill in all the required fields.")

st.header("Prediction Results")

# Display prediction results
if "prediction" in st.session_state:
    prediction = st.session_state["prediction"]
    st.success(f"Prediction Result: {prediction}")
    st.write("Note: You must have at least 5 credits in your core subjects.")
    if prediction in ["Likely", "Highly likely"]:
        st.write("Congratulations! You have a good chance of admission!")
    else:
        st.write("Consider the recommendations below for alternative options.")

# Display recommended alternatives
st.write("### Recommended Alternatives:")
if "recommendations" in st.session_state:
    recommendations = st.session_state["recommendations"]
    if isinstance(recommendations, list):
        for i, recommendation in enumerate(recommendations, start=1):
            st.write(f"{i}. {recommendation}")
    else:
        st.write("Unable to generate recommendations. Please try again later.")

st.header("About the Project")
st.write("""
  This AI-powered tool is designed to help Nigerian students make informed
  decisions about their university applications.
""")
