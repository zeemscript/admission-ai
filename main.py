import streamlit as st
import google.generativeai as genai


# Load API Key from environment variables
api_key = "AIzaSyCAOvmdRTfN9BCAWcACukXRItenG9t5sBA"  # Set GEMINI_API_KEY in your environment
if not api_key:
    st.error("API Key is missing. Set GEMINI_API_KEY as an environment variable.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Define expected response categories
EXPECTED_RESPONSES = {"Highly likely", "Likely", "Unlikely", "Highly unlikely"}


# Function to extract response text safely
def extract_response_text(response):
    try:
        return response.candidates[0].content.parts[0].text.strip()
    except (AttributeError, IndexError):
        return "Error: Could not extract response."


# Function to predict admission likelihood
def predict_admission(jamb_score, preferred_course, preferred_institution):
    prompt = f"""
    You are an expert in Nigerian university admissions. 

    Predict the admission likelihood for a student with:
    - JAMB score: {jamb_score}
    - Preferred Course: {preferred_course}
    - Preferred Institution: {preferred_institution}

    Respond with ONLY ONE of these: 'Highly likely', 'Likely', 'Unlikely', or 'Highly unlikely'.

    Example Outputs:
    - "Highly likely" → If the score is very high for the institution.
    - "Likely" → If the score is above average but not guaranteed.
    - "Unlikely" → If the score is below the cut-off.
    - "Highly unlikely" → If admission is almost impossible.
    """
    try:
        response = model.generate_content(prompt)
        result = extract_response_text(response)

        # Validate response
        return result if result in EXPECTED_RESPONSES else "Error: Unexpected response from AI."
    except Exception as e:
        return f"Error: {str(e)}"


# Function to generate alternative university recommendations
def generate_recommendations(jamb_score, preferred_course, preferred_institution):
    prompt = f"""
    A student wants to study '{preferred_course}' at '{preferred_institution}' but has a JAMB score of {jamb_score}.

    If their score is too low for admission, suggest four alternative universities and their courses.

    **Format response strictly as follows:**
    1. University Name - Alternative Course
    2. University Name - Alternative Course
    3. University Name - Alternative Course
    4. University Name - Alternative Course

    Do **not** add extra text outside this format.
    """
    try:
        response = model.generate_content(prompt)

        # Extract text properly
        recommendations = response.text.strip().split("\n") if hasattr(response, "text") else [
            "No recommendations available."]

        # Ensure valid formatting
        filtered_recommendations = [rec for rec in recommendations if "-" in rec]

        if len(filtered_recommendations) < 4:
            return ["Error: AI provided an invalid response."]

        return filtered_recommendations[:4]  # Ensure exactly 4 recommendations
    except Exception as e:
        return [f"Error: {str(e)}"]


# Initialize session state variables
if "prediction" not in st.session_state:
    st.session_state["prediction"] = None
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []

# Streamlit app
st.write("Disclaimer-------> Sometimes the Output might be wrong")
st.title("Nigerian University Admission Predictor 🎓")
st.subheader("Plan your future with confidence")
st.write("""
  This tool helps Nigerian students predict their chances of university admission.
""")

with st.sidebar:
    st.header("Enter Your Details")
    jamb_score = st.number_input("Enter your JAMB score:", min_value=0, max_value=400)
    preferred_course = st.text_input("Preferred Course:")
    preferred_institution = st.text_input("Preferred Institution:")

    if st.button("Submit"):
        if jamb_score and preferred_course and preferred_institution:
            st.write("🔄 Processing your request...")
            st.session_state["prediction"] = predict_admission(jamb_score, preferred_course, preferred_institution)
            st.session_state["recommendations"] = generate_recommendations(jamb_score, preferred_course,
                                                                           preferred_institution)
        else:
            st.error("⚠️ Please fill in all the required fields.")

st.header("📌 Prediction Results")

# Display prediction results
if st.session_state["prediction"]:
    prediction = st.session_state["prediction"]
    if "Error" in prediction:
        st.error(prediction)
    else:
        st.success(f"🎯 Prediction Result: {prediction}")
        st.write("ℹ️ Note: You must have at least 5 credits in your core subjects.")

        if prediction in ["Likely", "Highly likely"]:
            st.write("🎉 Congratulations! You have a good chance of admission!")
        else:
            st.write("⚠️ Consider the recommendations below for alternative options.")

# Display recommended alternatives
st.write("### 📌 Recommended Alternatives:")
st.write("Coming soon")
# if st.session_state["recommendations"]:
#     recommendations = st.session_state["recommendations"]
#     if "Error" in recommendations[0]:
#         st.error(recommendations[0])
#     else:
#         for i, recommendation in enumerate(recommendations, start=1):
#             st.write(f"{i}. {recommendation}")
# else:
#     st.write("No recommendations available.")

