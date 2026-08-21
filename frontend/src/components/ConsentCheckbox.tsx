export default function ConsentCheckbox({ checked, onChange }: { checked: boolean, onChange: (checked: boolean) => void }) {
  return (
    <label className="flex items-start gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-1 w-5 h-5 text-brand-gold rounded border-gray-300 focus:ring-brand-gold"
      />
      <span className="text-sm text-gray-700 leading-relaxed">
        I confirm I own this photo or have permission to use it, and I consent to it being processed to create my artwork. I understand my photo will be securely stored and deleted after 30 days. <a href="/privacy" className="text-brand-navy underline" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
      </span>
    </label>
  );
}
