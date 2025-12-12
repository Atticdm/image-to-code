import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
} from "../ui/select";
import { Badge } from "../ui/badge";
import StackLabel from "../core/StackLabel";
import { useRegistryStore } from "../../store/registry-store";

interface Props {
  stack: string | undefined;
  setStack: (config: string) => void;
  label?: string;
  shouldDisableUpdates?: boolean;
}

function OutputSettingsSection({
  stack,
  setStack,
  label = "Generating:",
  shouldDisableUpdates = false,
}: Props) {
  const { registry } = useRegistryStore();
  const stacks = registry?.stacks ?? [];
  return (
    <div className="flex flex-col gap-y-2 justify-between text-sm">
      <div className="grid grid-cols-3 items-center gap-4">
        <span>{label}</span>
        <Select
          value={stack}
          onValueChange={(value: string) => setStack(value)}
          disabled={shouldDisableUpdates || stacks.length === 0}
        >
          <SelectTrigger className="col-span-2" id="output-settings-js">
            {stack ? <StackLabel stack={stack} /> : "Select a stack"}
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {stacks.map((s) => (
                <SelectItem key={s.id} value={s.id}>
                  <div className="flex items-center">
                    <StackLabel stack={s.id} />
                    {s.in_beta && (
                      <Badge className="ml-2" variant="secondary">
                        Beta
                      </Badge>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}

export default OutputSettingsSection;
