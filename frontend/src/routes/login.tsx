import { createFileRoute } from '@tanstack/react-router'
import Main from "../components/Main"
import TitledSection from '../components/TitledSection'
import AsideNav from '../components/AsideNav'
import AsideLink from "../components/AsideLink"
import LoginForm from '../components/LoginForm'

export const Route = createFileRoute('/login')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <Main>
      <AsideNav>
        <AsideLink to="/login">Login</AsideLink>
        <AsideLink to="/register">Register</AsideLink>
      </AsideNav>
      <TitledSection title="Login" subtitle="">
        <LoginForm />
      </TitledSection>
    </Main>
  );
}