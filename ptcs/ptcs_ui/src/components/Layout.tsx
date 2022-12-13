import { NavLink as ReactRouterNavLink } from "react-router-dom";
import { AppShell, Header, Navbar, NavLink, Stack } from "@mantine/core";

export const Layout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <AppShell
      padding="md"
      navbar={
        <Navbar width={{ base: 300 }}>
          <Stack p="xs">
            {[
              { label: "Home", to: "/" },
              { label: "Settings", to: "/settings" },
            ].map((item) => (
              <ReactRouterNavLink
                to={item.to}
                style={{ textDecoration: "none" }}
              >
                {({ isActive }) => (
                  <NavLink
                    key={item.label}
                    label={item.label}
                    active={isActive}
                    sx={(theme) => ({
                      display: "flex",
                      alignItems: "center",
                      color: theme.colors.gray[7],
                      padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
                      borderRadius: theme.radius.md,
                      fontWeight: 500,
                    })}
                  />
                )}
              </ReactRouterNavLink>
            ))}
          </Stack>
        </Navbar>
      }
      header={
        <Header
          height={60}
          p="md"
          sx={(theme) => ({
            display: "flex",
            alignItems: "center",
            backgroundColor: theme.colors.blue[5],
            fontSize: 18,
            color: theme.white,
            fontWeight: 700,
          })}
        >
          Plarailers Train Control System
        </Header>
      }
    >
      {children}
    </AppShell>
  );
};
