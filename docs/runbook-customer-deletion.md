# GDPR Right to Erasure Runbook

## Overview
This runbook details the process for handling a customer's request to have their personal data deleted under the UK GDPR Right to Erasure (Right to be Forgotten).

## Timeline Requirements
Under UK GDPR, the organization must respond to and fulfill the deletion request within **30 days** of receipt.

## What is Deleted
- Raw user uploads from the `uploads-bucket` in S3.
- All AI-generated preview and production assets from the `generations-bucket` in S3.
- Customer name, email, and shipping address from the active database.

## What is Retained
- Anonymized order records.
- Financial transactions and anonymized payment data required for tax and legal compliance (typically retained for 7 years).

## Steps for Admin

1. **Verify Identity:**
   Ensure the request is coming from the authenticated email address associated with the orders.

2. **Locate Customer Records:**
   - Log into the Admin Dashboard.
   - Search for the customer's email to locate all associated Order IDs.

3. **Execute Deletion via Admin API:**
   - For each associated Order ID, invoke the photo deletion endpoint:
     `DELETE /api/admin/orders/{id}/photos`
   - This triggers a background task that permanently removes the S3 objects.
   - Anonymize the customer's PII on the Order record via the database or admin tooling (replace email/name with `[REDACTED]`).

4. **Verify Deletion is Complete:**
   - Confirm via the Admin Dashboard that the Order shows `Photos Deleted`.
   - Optionally, check the AWS S3 console to ensure objects for that order path no longer exist.

5. **Acknowledge Customer:**
   - Send the confirmation email.

## Template Acknowledgment Email

**Subject:** Confirmation of Data Deletion Request

Dear [Customer Name],

We have received and processed your request to delete your personal data from Wall Art.

We can confirm that all uploaded photos and generated artwork associated with your account have been permanently deleted from our servers. In accordance with legal and tax requirements, basic anonymized transaction records of your purchase have been retained, but these cannot be linked back to you or your imagery.

If you have any further questions, please reply to this email.

Best regards,
The Wall Art Privacy Team
