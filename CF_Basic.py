import streamlit as st
from abc import ABC, abstractmethod
import uuid
import re

class DataValidator:
    
    def __init__(self):
        self.patterns = {
            'name': r"^[A-Za-z\s\-']{2,50}$",
            
            'email': r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            
            'phone': r"^[\+]?[1-9]?[\d\s\-\(\)]{10,15}$",
            
            'campaign_title': r"^[A-Za-z0-9\s\-.,!?'\"()]{5,100}$",
            
            'location': r"^[A-Za-z0-9\s,.\-#]{3,100}$",
            
            'amount': r"^\d+(\.\d{1,2})?$",
            
            'medical_condition': r"^[A-Za-z\s\-()]{3,100}$",
               
            'organization': r"^[A-Za-z0-9\s\-.,&'\"()]{2,80}$"
        }
    
    def validate_pattern(self, pattern_name, input_text):
       
        if not input_text or not input_text.strip():
            return False, f"{pattern_name.replace('_', ' ').title()} cannot be empty"
        
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            return False, "Invalid validation pattern"
        
        if re.match(pattern, input_text.strip()):
            return True, ""
        else:
            return False, self._get_error_message(pattern_name)
    
    def _get_error_message(self, pattern_name):
        error_messages = {
            'name': "Name must contain only letters, spaces, hyphens, or apostrophes (2-50 characters)",
            'email': "Please enter a valid email address (e.g., user@example.com)",
            'phone': "Please enter a valid phone number (10-15 digits)",
            'campaign_title': "Title must be 5-100 characters with letters, numbers, and basic punctuation",
            'location': "Location must be 3-100 characters (letters, numbers, spaces, commas, periods)",
            'amount': "Amount must be a positive number with max 2 decimal places",
            'medical_condition': "Condition must be 3-100 characters (letters, spaces, hyphens, parentheses)",
            'organization': "Organization name must be 2-80 characters with basic punctuation allowed"
        }
        return error_messages.get(pattern_name, "Invalid input format")
    
    def validate_amount_range(self, amount_str, min_amount=1.0, max_amount=1000000.0):
        is_valid, error = self.validate_pattern('amount', amount_str)
        if not is_valid:
            return False, error
        
        try:
            amount = float(amount_str)
            if amount < min_amount:
                return False, f"Amount must be at least ${min_amount}"
            if amount > max_amount:
                return False, f"Amount cannot exceed ${max_amount:,.0f}"
            return True, ""
        except ValueError:
            return False, "Invalid amount format"

class Campaign(ABC):
    def __init__(self, title, target, creator_name, creator_email):
        self._id = str(uuid.uuid4())[:8]  # Encapsulated
        self.title = title
        self.target = target
        self.creator_name = creator_name
        self.creator_email = creator_email
        self.raised = 0
        self._donors = []  # Encapsulated
        self.validator = DataValidator()

    @abstractmethod
    def show_details(self):
        pass

    def add_donation(self, amount, donor_name, donor_email=None):
        self.raised += amount
        self._donors.append({
            'name': donor_name,
            'email': donor_email,
            'amount': amount
        })
        st.session_state.last_donation = f"Thanks {donor_name}! Donated ${amount} to {self.title}"

    def get_donors(self):
        return self._donors.copy()

class MedicalCampaign(Campaign):
    def __init__(self, title, target, creator_name, creator_email, patient_name, condition, hospital=None):
        super().__init__(title, target, creator_name, creator_email)
        self.patient_name = patient_name
        self.condition = condition
        self.hospital = hospital

    def show_details(self):
        progress = (self.raised / self.target) * 100
        st.subheader(f" Medical Campaign: {self.title}")
        st.write(f"**Patient:** {self.patient_name}")
        st.write(f"**Condition:** {self.condition}")
        if self.hospital:
            st.write(f"**Hospital:** {self.hospital}")
        st.write(f"**Campaign Creator:** {self.creator_name}")
        st.write(f"**Raised:** ${self.raised:,.2f} of ${self.target:,.2f} ({progress:.1f}%)")

class CommunityCampaign(Campaign):
    def __init__(self, title, target, creator_name, creator_email, location, organization=None):
        super().__init__(title, target, creator_name, creator_email)
        self.location = location
        self.organization = organization

    def show_details(self):
        progress = (self.raised / self.target) * 100
        st.subheader(f" Community Project: {self.title}")
        st.write(f"**Location:** {self.location}")
        if self.organization:
            st.write(f"**Organization:** {self.organization}")
        st.write(f"**Campaign Creator:** {self.creator_name}")
        st.write(f"**Raised:** ${self.raised:,.2f} of ${self.target:,.2f} ({progress:.1f}%)")

class CrowdPlatform:
    def __init__(self):
        self.validator = DataValidator()
        if 'campaigns' not in st.session_state:
            st.session_state.campaigns = []
            # Sample campaigns with validated data
            st.session_state.campaigns.append(
                MedicalCampaign("Cancer Treatment for Sarah", 50000, "John Smith", "john@example.com", 
                              "Sarah Johnson", "Breast Cancer Treatment", "City General Hospital")
            )
            st.session_state.campaigns.append(
                CommunityCampaign("Central Park Renovation", 20000, "Mary Wilson", "mary@parkfriends.org",
                                "Central Park, Downtown", "Friends of Central Park")
            )
            st.session_state.campaigns.append(
                MedicalCampaign("Heart Surgery Fund", 35000, "David Brown", "david@gmail.com",
                              "Michael Brown", "Heart Valve Replacement", "St. Mary's Medical Center")
            )
        if 'last_donation' not in st.session_state:
            st.session_state.last_donation = ""
        if 'campaign_type' not in st.session_state:
            st.session_state.campaign_type = "Medical"

    def add_campaign(self, campaign):
        st.session_state.campaigns.append(campaign)

    def list_campaigns(self):
        st.subheader(" Available Campaigns")
        for i, campaign in enumerate(st.session_state.campaigns, 1):
            progress = min(campaign.raised / campaign.target, 1.0)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{i}. {campaign.title}**")
                st.progress(progress)
                st.write(f"${campaign.raised:,.2f} of ${campaign.target:,.2f} raised ({progress*100:.1f}%)")
            with col2:
                campaign_type = " Medical" if isinstance(campaign, MedicalCampaign) else " Community"
                st.write(campaign_type)
            st.write("---")

def main():
    st.title(" Crowdfunding Platform")
    st.caption("Professional-grade funding website for noble purposes")
    
    platform = CrowdPlatform()

    # Show donation success message if exists
    if st.session_state.last_donation:
        st.success(st.session_state.last_donation)
        st.session_state.last_donation = ""  # Clear after showing

    menu = st.sidebar.selectbox(" Menu", ["Home", "View Campaigns", "Make Donation", "Create Campaign", "Validation Patterns"])

    if menu == "Home":
        st.header("Welcome to the best Crowdfunding Platform")
        st.write("Support causes you care about with confidence in our secure, and safe platform!")
        
        # Platform statistics
        total_campaigns = len(st.session_state.campaigns)
        total_raised = sum(c.raised for c in st.session_state.campaigns)
        total_donors = sum(len(c.get_donors()) for c in st.session_state.campaigns)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Campaigns", total_campaigns)
        with col2:
            st.metric("Total Raised", f"${total_raised:,.2f}")
        with col3:
            st.metric("Total Donors", total_donors)
        
        platform.list_campaigns()

    elif menu == "View Campaigns":
        st.header(" Campaign Details")
        if not st.session_state.campaigns:
            st.warning("No campaigns available yet")
        else:
            campaign_idx = st.selectbox(
                "Select a campaign to view details",
                options=[campaign.title for campaign in st.session_state.campaigns]
            )
            selected_campaign = next(c for c in st.session_state.campaigns if c.title == campaign_idx)
            selected_campaign.show_details()
            
            donors = selected_campaign.get_donors()
            if donors:
                st.subheader(" Recent Donors")
                for donor in donors[-5:]:
                    donor_email = donor.get('email', 'Anonymous')
                    st.write(f"- **{donor['name']}** donated ${donor['amount']:,.2f}")

    elif menu == "Make Donation":
        st.header(" Make a Donation")
        if not st.session_state.campaigns:
            st.warning("No campaigns available yet")
        else:
            campaign_idx = st.selectbox(
                "Select a campaign to donate to",
                options=[campaign.title for campaign in st.session_state.campaigns]
            )
            selected_campaign = next(c for c in st.session_state.campaigns if c.title == campaign_idx)
            selected_campaign.show_details()
            
            st.subheader("Donation Form")
            with st.form("donation_form"):
                donor_name = st.text_input("Your Full Name *", placeholder="e.g., John Smith")
                donor_email = st.text_input("Email Address", placeholder="e.g., john@example.com")
                donor_phone = st.text_input("Phone Number (Optional)", placeholder="e.g., +1-555-123-4567")
                amount_str = st.text_input("Donation Amount ($) *", placeholder="e.g., 100.00")
                
                st.write("*Required fields")
                
                if st.form_submit_button("💳 Donate Now"):
                    # Validate all inputs
                    errors = []
                    
                    # Validate name
                    name_valid, name_error = platform.validator.validate_pattern('name', donor_name)
                    if not name_valid:
                        errors.append(f"Name: {name_error}")
                    
                    # Validate email if provided
                    if donor_email:
                        email_valid, email_error = platform.validator.validate_pattern('email', donor_email)
                        if not email_valid:
                            errors.append(f"Email: {email_error}")
                    
                    # Validate phone if provided
                    if donor_phone:
                        phone_valid, phone_error = platform.validator.validate_pattern('phone', donor_phone)
                        if not phone_valid:
                            errors.append(f"Phone: {phone_error}")
                    
                    # Validate amount
                    amount_valid, amount_error = platform.validator.validate_amount_range(amount_str, 1.0, 50000.0)
                    if not amount_valid:
                        errors.append(f"Amount: {amount_error}")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        amount = float(amount_str)
                        selected_campaign.add_donation(amount, donor_name, donor_email)
                        st.rerun()

    elif menu == "Create Campaign":
        st.header(" Create New Campaign")
        
        # Campaign type selection
        campaign_type = st.radio(
            "Campaign Type",
            ("Medical", "Community"),
            index=0 if st.session_state.campaign_type == "Medical" else 1,
            key="campaign_type_radio",
            on_change=lambda: st.session_state.update({"campaign_type": st.session_state.campaign_type_radio})
        )
        
        with st.form("create_campaign"):
            st.subheader("Campaign Creator Information")
            creator_name = st.text_input("Your Full Name *", placeholder="e.g., John Smith")
            creator_email = st.text_input("Your Email Address *", placeholder="e.g., john@example.com")
            
            st.subheader("Campaign Details")
            title = st.text_input("Campaign Title *", placeholder="e.g., Help Sarah Beat Cancer")
            target_str = st.text_input("Target Amount ($) *", placeholder="e.g., 25000.00")
            
            # Dynamic fields based on campaign type
            if st.session_state.campaign_type == "Medical":
                st.subheader("Medical Campaign Specific")
                patient_name = st.text_input("Patient Name *", placeholder="e.g., Sarah Johnson")
                condition = st.text_input("Medical Condition *", placeholder="e.g., Breast Cancer Treatment")
                hospital = st.text_input("Hospital/Medical Center", placeholder="e.g., City General Hospital")
            else:
                st.subheader("Community Campaign Specific")
                location = st.text_input("Project Location *", placeholder="e.g., Central Park, Downtown")
                organization = st.text_input("Organization Name", placeholder="e.g., Friends of Central Park")
            
            st.write("*Required fields")
            
            if st.form_submit_button(" Create Campaign"):
                # Validate all inputs
                errors = []
                
                # Common validations
                name_valid, name_error = platform.validator.validate_pattern('name', creator_name)
                if not name_valid:
                    errors.append(f"Creator Name: {name_error}")
                
                email_valid, email_error = platform.validator.validate_pattern('email', creator_email)
                if not email_valid:
                    errors.append(f"Creator Email: {email_error}")
                
                title_valid, title_error = platform.validator.validate_pattern('campaign_title', title)
                if not title_valid:
                    errors.append(f"Campaign Title: {title_error}")
                
                target_valid, target_error = platform.validator.validate_amount_range(target_str, 100.0, 1000000.0)
                if not target_valid:
                    errors.append(f"Target Amount: {target_error}")
                
                # Type-specific validations
                if st.session_state.campaign_type == "Medical":
                    patient_valid, patient_error = platform.validator.validate_pattern('name', patient_name)
                    if not patient_valid:
                        errors.append(f"Patient Name: {patient_error}")
                    
                    condition_valid, condition_error = platform.validator.validate_pattern('medical_condition', condition)
                    if not condition_valid:
                        errors.append(f"Medical Condition: {condition_error}")
                    
                    if hospital:
                        hospital_valid, hospital_error = platform.validator.validate_pattern('organization', hospital)
                        if not hospital_valid:
                            errors.append(f"Hospital: {hospital_error}")
                else:
                    location_valid, location_error = platform.validator.validate_pattern('location', location)
                    if not location_valid:
                        errors.append(f"Location: {location_error}")
                    
                    if organization:
                        org_valid, org_error = platform.validator.validate_pattern('organization', organization)
                        if not org_valid:
                            errors.append(f"Organization: {org_error}")
                
                if errors:
                    st.error("Please fix the following errors:")
                    for error in errors:
                        st.error(f"• {error}")
                else:
                    target_amount = float(target_str)
                    if st.session_state.campaign_type == "Medical":
                        new_campaign = MedicalCampaign(
                            title, target_amount, creator_name, creator_email,
                            patient_name, condition, hospital if hospital else None
                        )
                    else:
                        new_campaign = CommunityCampaign(
                            title, target_amount, creator_name, creator_email,
                            location, organization if organization else None
                        )
                    
                    platform.add_campaign(new_campaign)
                    st.success(f" {st.session_state.campaign_type} campaign created successfully!")
                    st.balloons()
                    st.rerun()

    elif menu == "Validation Patterns":
        st.header(" RegEx Validation Patterns Reference")
        st.write("Here are the regular expression patterns used for data validation in our platform:")
        
        validator = DataValidator()
        
        for pattern_name, pattern in validator.patterns.items():
            with st.expander(f" {pattern_name.replace('_', ' ').title()} Pattern"):
                st.code(pattern, language="regex")
                st.write(f"**Purpose:** {validator._get_error_message(pattern_name)}")
                
                # Test the pattern
                st.write("**Test this pattern:**")
                test_input = st.text_input(f"Enter test text for {pattern_name}", key=f"test_{pattern_name}")
                if test_input:
                    is_valid, error_msg = validator.validate_pattern(pattern_name, test_input)
                    if is_valid:
                        st.success(" Valid input!")
                    else:
                        st.error(f" {error_msg}")

if __name__ == "__main__":
    main()