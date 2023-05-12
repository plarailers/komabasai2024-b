import { AppShell, Header } from "@mantine/core";

export const Layout: React.FC<React.PropsWithChildren> = ({ children }) => {
  return (
    <AppShell
      padding="md"
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
