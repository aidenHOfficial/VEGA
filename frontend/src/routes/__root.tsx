import { createRootRoute, Outlet } from "@tanstack/react-router";

function RootLayout() {
  return <Outlet />;
}

function NotFound() {
  return (
    <section className="max-w-3xl mx-auto text-center pt-16">
      <h1 className="text-4xl font-bold">
        not found :(
      </h1>
      <p>the page you are searching for does not exist</p>
    </section>
  );
}

export const Route = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFound,
});
