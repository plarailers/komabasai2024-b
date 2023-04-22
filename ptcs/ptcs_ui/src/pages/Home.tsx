import { Code, Container } from "@mantine/core";
import { DefaultService, RailwayState } from "ptcs_client";
import { Layout } from "../components/Layout";
import { useEffect, useState } from "react";
import Platform from "../components/Platform";
import Section from "../components/Section";
import Railway from "../components/Railway";

const Home: React.FC = () => {
  const [data, setData] = useState<RailwayState | null>(null);
  const [time, setTime] = useState<Date>();

  useEffect(() => {
    const interval = setInterval(() => {
      DefaultService.getState().then((state) => {
        setData(state);
        setTime(new Date());
      });
    }, 1000);
    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <Layout>
      <Container>
        {time?.toLocaleString()}
        <Railway width={680} height={160}>
          <Platform position={{ x: 340, y: 90 }} />

          <Section
            id="s0"
            points={[
              { x: 160, y: 100 },
              { x: 120, y: 100 },
              { x: 100, y: 120 },
              { x: 40, y: 120 },
              { x: 40, y: 40 },
              { x: 100, y: 40 },
              { x: 120, y: 60 },
              { x: 200, y: 60 },
            ]}
          />
          <Section
            id="s1"
            points={[
              { x: 200, y: 60 },
              { x: 240, y: 60 },
            ]}
          />
          <Section
            id="s2"
            points={[
              { x: 240, y: 60 },
              { x: 440, y: 60 },
            ]}
          />
          <Section
            id="s3"
            points={[
              { x: 440, y: 60 },
              { x: 480, y: 60 },
            ]}
          />
          <Section
            id="s4"
            points={[
              { x: 480, y: 60 },
              { x: 560, y: 60 },
              { x: 580, y: 40 },
              { x: 640, y: 40 },
              { x: 640, y: 120 },
              { x: 580, y: 120 },
              { x: 560, y: 100 },
              { x: 520, y: 100 },
            ]}
          />
          <Section
            id="s5"
            points={[
              { x: 520, y: 100 },
              { x: 400, y: 100 },
            ]}
          />
          <Section
            id="s6"
            points={[
              { x: 400, y: 100 },
              { x: 380, y: 120 },
              { x: 300, y: 120 },
              { x: 280, y: 100 },
            ]}
          />
          <Section
            id="s7"
            points={[
              { x: 280, y: 100 },
              { x: 160, y: 100 },
            ]}
          />
          <Section
            id="s8"
            points={[
              { x: 160, y: 100 },
              { x: 200, y: 60 },
            ]}
          />
          <Section
            id="s9"
            points={[
              { x: 240, y: 60 },
              { x: 280, y: 100 },
            ]}
          />
          <Section
            id="s10"
            points={[
              { x: 400, y: 100 },
              { x: 440, y: 60 },
            ]}
          />
          <Section
            id="s11"
            points={[
              { x: 480, y: 60 },
              { x: 520, y: 100 },
            ]}
          />
        </Railway>
        <Code block>{JSON.stringify(data, null, 4)}</Code>
      </Container>
    </Layout>
  );
};

export default Home;
