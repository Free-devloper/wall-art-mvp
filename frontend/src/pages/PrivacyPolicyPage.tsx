export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 prose prose-blue">
      <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>
      <p>Last updated: {new Date().toLocaleDateString()}</p>
      <h2 className="text-2xl font-semibold mt-8 mb-4">1. Data Collected</h2>
      <p>We collect your email, name, shipping address, and the photo you upload. We use Stripe for payment processing and do not store your credit card information.</p>
      <h2 className="text-2xl font-semibold mt-8 mb-4">2. How Photos Are Processed</h2>
      <p>Your uploaded photos are processed securely using AI models to generate your artwork. The original photos are not used to train our AI.</p>
      <h2 className="text-2xl font-semibold mt-8 mb-4">3. Storage & Retention</h2>
      <p>Your original photos and generated artworks are stored securely. We automatically delete your original uploaded photo 30 days after your order is completed.</p>
      <h2 className="text-2xl font-semibold mt-8 mb-4">4. Third-Party Processors</h2>
      <p>We share your delivery details with our shipping partners. We do not sell your data to any third party.</p>
      <h2 className="text-2xl font-semibold mt-8 mb-4">5. Your Rights</h2>
      <p>Under UK GDPR, you have the right to access, rectify, or erase your personal data. Contact us to exercise these rights.</p>
      <h2 className="text-2xl font-semibold mt-8 mb-4">6. Contact Info</h2>
      <p>If you have any questions, please contact support@wallart.example.com.</p>
    </div>
  );
}
