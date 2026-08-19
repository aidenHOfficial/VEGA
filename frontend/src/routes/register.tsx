import { createFileRoute } from '@tanstack/react-router'
import Main from '../components/Main';
import AsideNav from '../components/AsideNav';
import AsideLink from '../components/AsideLink';
import TitledSection from '../components/TitledSection';
import RegisterForm from '../components/RegisterForm';

export const Route = createFileRoute('/register')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <Main>
      <AsideNav>
        <AsideLink to="/login">Login</AsideLink>
        <AsideLink to="/register">Register</AsideLink>
      </AsideNav>
      <TitledSection title="Register" subtitle="">
        <RegisterForm />
      </TitledSection>
    </Main>
  );
}
