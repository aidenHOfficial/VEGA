export default function TitledSection({ title, subtitle = null, children }: React.PropsWithChildren<{ title: string, subtitle : string | null }>) {
  return (
    <section className="w-full flex flex-col items-center h-screen">
    <h1 className="text-3xl">{title}</h1>
    <p className="text-sm">
       {subtitle} 
    </p>
    <br></br>
    {children}
    </section>
  );
}