import * as Dialog from "@radix-ui/react-dialog";

import { Button } from "@/components/ui/button";
import { Loader } from "@/components/loader";

interface ConfirmationDialogProps {
  title: string;
  description: string;
  confirmLabel: string;
  isOpen: boolean;
  isPending?: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export function ConfirmationDialog({
  title,
  description,
  confirmLabel,
  isOpen,
  isPending = false,
  onOpenChange,
  onConfirm,
}: ConfirmationDialogProps) {
  return (
    <Dialog.Root onOpenChange={onOpenChange} open={isOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/40" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white p-6 shadow-xl focus:outline-none">
          <Dialog.Title className="text-lg font-bold text-slate-950">{title}</Dialog.Title>
          <Dialog.Description className="mt-2 text-sm leading-6 text-slate-600">{description}</Dialog.Description>
          <div className="mt-6 flex justify-end gap-3">
            <Dialog.Close asChild>
              <Button disabled={isPending} variant="outline">Cancel</Button>
            </Dialog.Close>
            <Button disabled={isPending} onClick={onConfirm} variant="danger">
              {isPending && <Loader className="mr-2 size-4 border-rose-200 border-t-white" />}
              {confirmLabel}
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
