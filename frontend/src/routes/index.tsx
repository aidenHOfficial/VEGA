import { createFileRoute } from "@tanstack/react-router";
import Main from "../components/Main"

export const Route = createFileRoute("/")({
  component: Home,
});

const appDesc = "This application is a Python, MySQL / SQLModel, FastAPI, React, Tailwind application";

function Home() {
  return (
    <Main>
        Hello World!
    </Main>
  );
}