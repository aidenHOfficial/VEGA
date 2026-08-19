import { Link } from "@tanstack/react-router";

type AsideLinkProps = React.PropsWithChildren<{
  to: string;
  className?: string;
  indented?: boolean;
}>;

export default function AsideLink({ to, children, className = "", indented = false}: AsideLinkProps) {
  const base = "bg-primary transition-colors underline text-center";

  return (
    <div className={`flex flex-row w-full ${indented ? "justify-end" : "justify-start"}`}>
      <Link to={to} className={`${base} ${className} ${indented ? "w-4/5" : "w-full"}`}>
        {children}
      </Link>
    </div>
  );
}