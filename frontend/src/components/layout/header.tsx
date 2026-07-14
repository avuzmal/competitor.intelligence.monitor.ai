"use client";

import { signOut } from "next-auth/react";
import { LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Header({ user }: { user: any }) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
      <div className="flex flex-1 items-center justify-end gap-4">
        <div className="flex items-center gap-2 text-sm font-medium">
          <User className="h-5 w-5 text-muted-foreground" />
          <span>{user?.name || user?.email}</span>
        </div>
        <Button variant="outline" size="icon" onClick={() => signOut()}>
          <LogOut className="h-4 w-4" />
          <span className="sr-only">Sign out</span>
        </Button>
      </div>
    </header>
  );
}
