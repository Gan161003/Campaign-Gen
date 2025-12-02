import streamlit as st
import pandas as pd

# ---------------------------------------------------
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(page_title="Campaign Tool", layout="wide", page_icon="✨")

# Initialize session state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "generator"

# ---------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------
st.markdown(
    """
    <div style="text-align:center; padding: 10px;">
        <h1 style="color:#2e4a7d; font-weight:700;">✨ Campaign Generative Tool</h1>
        <p style="font-size:18px;">Create or validate campaign naming conventions.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation Buttons
col1, col2, col3 = st.columns([2,1,2])
with col2:
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("🎨 Generator"):
            st.session_state.active_tab = "generator"
    with nav2:
        if st.button("🧪 Validator"):
            st.session_state.active_tab = "validator"

st.markdown("---")


# ---------------------------------------------------
# TAB 1 — GENERATOR
# ---------------------------------------------------
if st.session_state.active_tab == "generator":

    st.subheader("🎨 Campaign Generator")

    uploaded_file = st.file_uploader("📁 Upload CSV / Excel File", type=["csv", "xlsx", "xls"])

    if uploaded_file:

        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("File uploaded successfully!")
        st.write("### 🔍 Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        st.subheader("🎛 Filters")

        # Auto-select only object/string columns
        filter_cols = [c for c in df.columns if df[c].dtype == "object"]
        filters = {}
        cols = st.columns(3)

        for i, col in enumerate(filter_cols):
            vals = sorted(df[col].dropna().unique().tolist())
            filters[col] = cols[i % 3].multiselect(col, vals)

        filtered_df = df.copy()

        # Apply filters
        for col, selected_vals in filters.items():
            if selected_vals:
                filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

        st.subheader("⚡ Generate Campaign Names")

        if st.button("Generate Now"):

            if filtered_df.empty:
                st.error("No matching rows. Adjust filters.")
            else:

                # REQUIRED fields for naming
                required_cols = [
                    "region", "market", "channel", "audience", "creative",
                    "ad_type", "ad_format", "objective", "device", "placement"
                ]

                usable = [c for c in required_cols if c in filtered_df.columns]

                def make_name(row):
                    parts = []
                    for c in usable:
                        v = str(row[c]).replace(" ", "").replace("-", "").strip()
                        parts.append(v)
                    return "_".join(parts)

                # Generate new column
                filtered_df["Campaign id's"] = filtered_df.apply(make_name, axis=1)

                # ---------------------------------------------------------
                # Move Generated Column to FIRST
                # ---------------------------------------------------------
                cols_order = ["Campaign id's"] + [
                    c for c in filtered_df.columns if c != "Campaign id's"
                ]
                filtered_df = filtered_df[cols_order]

                st.success("Names Generated Successfully!")

                st.write("### 📌 Generated Campaign Names")
                st.dataframe(filtered_df, use_container_width=True)

                # ---------------------------------------------------------
                # Download button moved BELOW the table
                # ---------------------------------------------------------
                st.write("### ⬇ Download CSV")
                csv = filtered_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "generated_campaigns.csv", "text/csv")


# ---------------------------------------------------
# TAB 2 — VALIDATOR
# ---------------------------------------------------
elif st.session_state.active_tab == "validator":

    st.subheader("🧪 Campaign Validator")

    expected = [
        "region", "market", "channel", "audience", "creative",
        "ad_type", "ad_format", "objective", "device", "placement"
    ]

    st.info(f"Expected Format → `{'_'.join(expected)}`")

    input_text = st.text_input("Enter Campaign Name")

    if st.button("Validate"):
        if not input_text.strip():
            st.warning("Please enter a name.")
        else:
            parts = input_text.split("_")

            if len(parts) != len(expected):
                st.error("❌ Wrong number of parts")
                st.write(f"Expected {len(expected)}, got {len(parts)}")
            else:
                st.success("✔ Valid Campaign Format")

            st.write("### Breakdown")
            breakdown = {expected[i]: parts[i] if i < len(parts) else "" for i in range(len(expected))}
            st.json(breakdown)
