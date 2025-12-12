import React from "react";
import { getStackComponentsFromRegistry } from "../../lib/backendRegistry";
import { useRegistryStore } from "../../store/registry-store";

interface StackLabelProps {
  stack: string;
}

const StackLabel: React.FC<StackLabelProps> = ({ stack }) => {
  const { registry } = useRegistryStore();
  const stackComponents = getStackComponentsFromRegistry(registry, stack);
  const displayParts = stackComponents.length ? stackComponents : [stack];

  return (
    <div>
      {displayParts.map((component, index) => (
        <React.Fragment key={index}>
          <span className="font-semibold">{component}</span>
          {index < displayParts.length - 1 && " + "}
        </React.Fragment>
      ))}
    </div>
  );
};

export default StackLabel;
