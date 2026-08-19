export default function Main({ children }: React.PropsWithChildren) {
  return (
    <main className="w-full min-h-screen flex flex-row">
      {children}
    </main>
  );
}