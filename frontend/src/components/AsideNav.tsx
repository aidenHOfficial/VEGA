import AsideLink from "../components/AsideLink"

export default function AsideNav({children}: React.PropsWithChildren) {
    return (
        <aside className="max-h-full w-1/5 bg-gray-300 pt-10">
            <nav className="flex flex-col gap-2 justify-center">
                <AsideLink to="/">Pony Express</AsideLink>
                {children}
            </nav>
        </aside>
    )
}