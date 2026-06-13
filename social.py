import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Define the CSV file to store social protection registry entries
SOCIAL_DATA_FILE = 'sokoto_social_protection_registry_2026.csv'

SOKOTO_LGAS = [
    "Select LGA", "Binji", "Bodinga", "Dange Shuni", "Gada", "Goronyo", 
    "Gudu", "Gwadabawa", "Illela", "Isa", "Kware", "Kebbe", "Rabah", 
    "Sabon Birni", "Shagari", "Silame", "Sokoto North", "Sokoto South", 
    "Tambuwal", "Tangaza", "Tureta", "Wamako", "Wurno", "Yabo"
]

INTERVENTION_TYPES = [
    "Select Intervention", 
    "Unconditional Cash Transfer (UCT)", 
    "Conditional Cash Transfer (Education)", 
    "Basic Health Insurance Subsidy", 
    "Agricultural Input Subsidy", 
    "Livelihood Grant / SME Support",
    "Nutritional Food Support"
]

VULNERABILITY_CATEGORIES = [
    "Select Category",
    "Female-Headed Household",
    "Elderly Individual (60+)",
    "Person with Disability (PWD)",
    "Unemployed Youth Headed",
    "IDP / Conflict Affected",
    "Low-Income / Poor Household"
]

def load_social_data():
    required_columns = [
        'Timestamp', 'State', 'LGA', 'Cluster / Ward', 'Household ID', 
        'Beneficiary Name', 'Sex of Head', 'Vulnerability Category', 
        'Intervention Type', 'Budget Allocated (NGN)', 'Amount Disbursed (NGN)', 'Contact Phone'
    ]
    
    if os.path.exists(SOCIAL_DATA_FILE):
        df = pd.read_csv(SOCIAL_DATA_FILE)
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            for col in missing_cols:
                df[col] = None
            df.to_csv(SOCIAL_DATA_FILE, index=False)
        return df
    return pd.DataFrame(columns=required_columns)

def save_social_data(df):
    df.to_csv(SOCIAL_DATA_FILE, index=False)

# --- App Configuration ---
st.set_page_config(page_title="Sokoto Social Protection Registry", layout="wide", page_icon="🏛️")

# Custom CSS styling for an official Ministry look
st.markdown("""
    <style>
    .main-title { font-size:36px !important; font-weight: bold; color: #065F46; }
    .section-header { font-size:22px !important; font-weight: 600; color: #1E3A8A; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🏛️ Ministry of Budget and Economic Planning, Sokoto</p>', unsafe_allow_html=True)
st.subheader('Social Protection Interventions & Beneficiary Registry')
st.markdown("---")

current_df = load_social_data()

# --- TOP ROW: STRATEGIC PLANNING METRICS ---
if not current_df.empty:
    total_beneficiaries = len(current_df)
    total_allocated = pd.to_numeric(current_df['Budget Allocated (NGN)']).sum()
    total_disbursed = pd.to_numeric(current_df['Amount Disbursed (NGN)']).sum()
    unqiue_lgas = current_df['LGA'].dropna().nunique()
    
    # Financial metrics display
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Total Households Enrolled", total_beneficiaries)
    m2.metric("💰 Total Budget Allocated", f"₦{total_allocated:,.2f}")
    m3.metric("📈 Total Funds Disbursed", f"₦{total_disbursed:,.2f}")
    m4.metric("🗺️ LGAs Reached", f"{unqiue_lgas} / 23")
    st.markdown("---")

col1, col2 = st.columns([3, 2])

# --- COLUMN 1: INTERVENTION REGISTRATION FORM ---
with col1:
    st.markdown('<p class="section-header">📝 Beneficiary Intake & Allocation Logging</p>', unsafe_allow_html=True)
    
    if "form_generation" not in st.session_state:
        st.session_state.form_generation = 0

    with st.form(key=f'social_form_gen_{st.session_state.form_generation}', clear_on_submit=False):
        st.markdown("##### 📍 Geographic & Administrative Identifiers")
        geo_col1, geo_col2, geo_col3 = st.columns(3)
        with geo_col1:
            state = st.text_input('State', value='Sokoto', disabled=True)
        with geo_col2:
            lga = st.selectbox('Local Government Area (LGA)', options=SOKOTO_LGAS)
        with geo_col3:
            ward = st.text_input('Ward / Cluster Name')
            
        st.markdown("##### 👥 Beneficiary Household Profile")
        profile_col1, profile_col2 = st.columns([2, 1])
        with profile_col1:
            name = st.text_input('Household Representative Name')
            vulnerability = st.selectbox('Primary Vulnerability Status', options=VULNERABILITY_CATEGORIES)
        with profile_col2:
            hh_id = st.text_input('Household ID / Code')
            sex = st.selectbox('Sex of Head', options=['Select', 'Male', 'Female'])
            
        st.markdown("##### 💳 Financial & Intervention Framework")
        fin_col1, fin_col2, fin_col3 = st.columns(3)
        with fin_col1:
            intervention = st.selectbox('Intervention Program', options=INTERVENTION_TYPES)
        with fin_col2:
            budget = st.number_input('Budget Allocated (NGN)', min_value=0.0, value=50000.0, step=1000.0)
        with fin_col3:
            disbursed = st.number_input('Initial Amount Disbursed (NGN)', min_value=0.0, value=25000.0, step=1000.0)
            
        phone_number = st.text_input('Contact Phone Number')
        
        st.markdown(" ")
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            submitted = st.form_submit_button('Commit Registry Entry', type='primary')
        with btn_col2:
            clear_submitted = st.form_submit_button('Reset Blank Layout')

        if clear_submitted:
            st.session_state.form_generation += 1
            st.rerun()

        if submitted:
            if lga != 'Select LGA' and intervention != 'Select Intervention' and vulnerability != 'Select Category' and hh_id and name and sex != 'Select' and phone_number:
                if disbursed > budget:
                    st.error('❌ Data Conflict: Disbursed amount cannot exceed total allocated program budget.')
                else:
                    new_record = pd.DataFrame([{
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'State': state,
                        'LGA': lga,
                        'Cluster / Ward': ward,
                        'Household ID': hh_id,
                        'Beneficiary Name': name,
                        'Sex of Head': sex,
                        'Vulnerability Category': vulnerability,
                        'Intervention Type': intervention,
                        'Budget Allocated (NGN)': float(budget),
                        'Amount Disbursed (NGN)': float(disbursed),
                        'Contact Phone': phone_number
                    }])
                    
                    updated_df = pd.concat([current_df, new_record], ignore_index=True)
                    save_social_data(updated_df)
                    
                    st.session_state.form_generation += 1
                    st.success(f'✅ Successfully registered intervention package for {name}.')
                    st.rerun()
            else:
                st.error('❌ Validation Failure: Complete all options, assign classifications, and verify identifiers.')

# --- COLUMN 2: EXCISE CONTROLS & VISUAL PLANNING ANALYTICS ---
with col2:
    st.markdown('<p class="section-header">🛠️ Registry Configuration</p>', unsafe_allow_html=True)
    
    with st.expander("❌ Void or Revoke Erroneous Allocation Entry"):
        with st.form('registry_removal_form'):
            if not current_df.empty:
                current_df['Select_Label'] = current_df['LGA'].astype(str) + " | HH: " + current_df['Household ID'].astype(str) + " | " + current_df['Beneficiary Name'].astype(str)
                label_to_remove = st.selectbox('Select Specific Context to Void', options=current_df['Select_Label'].unique())
                
                matching_rows = current_df[current_df['Select_Label'] == label_to_remove]
                remove_submitted = st.form_submit_button('Permanently Revoke Entry', type='secondary')
                
                if remove_submitted and not matching_rows.empty:
                    target_row = matching_rows.iloc[0]
                    updated_df = current_df[
                        ~((current_df['LGA'] == target_row['LGA']) & 
                          (current_df['Household ID'] == target_row['Household ID']) & 
                          (current_df['Beneficiary Name'] == target_row['Beneficiary Name']))
                    ]
                    if 'Select_Label' in updated_df.columns:
                        updated_df = updated_df.drop(columns=['Select_Label'])
                    save_social_data(updated_df)
                    st.success('🗑️ Allocation reference scrubbed from active registry.')
                    st.rerun()
            else:
                st.info("Roster empty.")

    st.markdown('<p class="section-header">📊 Enrolled Households by LGA</p>', unsafe_allow_html=True)
    if not current_df.empty:
        lga_counts = current_df['LGA'].dropna().value_counts()
        if not lga_counts.empty:
            st.bar_chart(lga_counts, color="#065F46")
        else:
            st.info("Awaiting structural inputs.")
    else:
        st.info("No field data available.")

# --- SECTION 3: FINANCIALLY AUDITED MASTER DATA VIEW ---
st.markdown("---")
st.markdown('<p class="section-header">📋 Audited Master Ledger & Disbursement Progress Infographic</p>', unsafe_allow_html=True)

if 'Select_Label' in current_df.columns:
    current_df = current_df.drop(columns=['Select_Label'])

if not current_df.empty:
    infographic_df = current_df.copy()
    
    # Calculate a dynamic tracking index representing percent execution of funding per record
    infographic_df['Disbursement Ratio (%)'] = (
        infographic_df['Amount Disbursed (NGN)'].astype(float) / 
        infographic_df['Budget Allocated (NGN)'].astype(float) * 100.0
    ).fillna(0)

    st.data_editor(
        infographic_df.sort_values(by="Timestamp", ascending=False),
        column_config={
            "Disbursement Ratio (%)": st.column_config.ProgressColumn(
                "Funding Payout Progress Bar",
                help="Tracks fraction of household allocated budget securely distributed to date",
                format="%d%%",
                min_value=0,
                max_value=100,
                color="green"
            )
        },
        disabled=True,
        use_container_width=True
    )
    
    csv_buffer = current_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Certified Master Social Protection Ledger (CSV)",
        data=csv_buffer,
        file_name=f"Sokoto_Social_Protection_Master_Ledger_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info('The master protection framework roster is completely empty right now.')