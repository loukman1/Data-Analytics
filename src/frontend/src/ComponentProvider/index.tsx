import React, { FC } from "react";
import { Home } from "../Home";

// Component das zuerst Angezeigt wird
const startComponent = Home;

type ComponentContextType = {
  current: FC;
  setCurrent: (next: FC) => void;
};

export const ComponentContext = React.createContext<
  ComponentContextType | undefined
>(undefined);

interface Props {}

/**
 * Component das den Component Context verwendet um Funktionen bereit zustellen
 * um das Aktuelle Component auszuwählen.
 */
export const ComponentProvider: React.FC<Props> = ({ children }) => {
  const [current, setCurrent] = React.useState<FC>(startComponent);

  const handleSetCurrent = (next: FC) => {
    setCurrent(next);
  };

  return (
    <ComponentContext.Provider
      value={{ current, setCurrent: handleSetCurrent }}
    >
      {children}
    </ComponentContext.Provider>
  );
};
