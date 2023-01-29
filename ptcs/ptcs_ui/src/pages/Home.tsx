import { Code, Container } from "@mantine/core";
import { Layout } from "../components/Layout";
import { useEffect, useState } from "react";

const Home: React.FC = () => {
  const [data, setData] = useState(null);
  const [time, setTime] = useState<Date>();

  useEffect(() => {
    setInterval(() => {
      fetch("/api/state")
        .then((res) => res.json())
        .then((data) => {
          setData(data);
          setTime(new Date());
        });
    }, 1000);
  }, []);

  return (
    <Layout>
      <Container>
        hello
        <Code block>{JSON.stringify(data)}</Code>
        {time?.toLocaleString()}
      </Container>
    </Layout>
  );
};

export default Home;
