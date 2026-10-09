function ErrorMessage({ title = 'Something went wrong', message }) {
  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      <p className="font-semibold">{title}</p>
      {message ? <p className="mt-1">{message}</p> : null}
    </div>
  );
}

export default ErrorMessage;
