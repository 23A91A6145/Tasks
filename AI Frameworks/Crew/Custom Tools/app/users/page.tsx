"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, UserMinus, UserPlus } from "lucide-react";

import { apiFetch, type Member } from "@/lib/api";
import { useSession } from "@/lib/session";
import { formatDate } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Dropdown, DropdownItem } from "@/components/ui/dropdown";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

const ROLES = ["owner", "admin", "manager", "agent", "user"] as const;

const roleBadge: Record<string, "default" | "secondary" | "success" | "warning" | "destructive"> = {
  owner: "default",
  admin: "success",
  manager: "warning",
  agent: "secondary",
  user: "secondary",
};

export default function UsersPage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<string>("agent");
  const [inviting, setInviting] = useState(false);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [confirmRemove, setConfirmRemove] = useState<string | null>(null);

  const canManage =
    activeWorkspace?.your_role === "owner" || activeWorkspace?.your_role === "admin";

  const load = useCallback(() => {
    if (!activeWorkspace) return;
    setLoading(true);
    apiFetch<Member[]>(`/api/v1/workspaces/${activeWorkspace.slug}/members`)
      .then(setMembers)
      .finally(() => setLoading(false));
  }, [activeWorkspace]);

  useEffect(() => {
    load();
  }, [load]);

  const invite = async () => {
    if (!inviteEmail.trim()) return;
    setInviting(true);
    try {
      await apiFetch(`/api/v1/workspaces/${activeWorkspace?.slug}/members`, {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail.trim(), role: inviteRole }),
      });
      toast({ title: "Member added", variant: "success" });
      setInviteOpen(false);
      setInviteEmail("");
      load();
    } catch (error) {
      toast({
        title: "Could not add member",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    } finally {
      setInviting(false);
    }
  };

  const changeRole = async (member: Member, role: string) => {
    try {
      await apiFetch(`/api/v1/workspaces/${activeWorkspace?.slug}/members/${member.user.id}`, {
        method: "PATCH",
        body: JSON.stringify({ role }),
      });
      toast({ title: "Role updated", variant: "success" });
      load();
    } catch (error) {
      toast({
        title: "Could not update role",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    }
  };

  const remove = async (member: Member) => {
    setRemovingId(member.user.id);
    try {
      await apiFetch(`/api/v1/workspaces/${activeWorkspace?.slug}/members/${member.user.id}`, {
        method: "DELETE",
      });
      toast({ title: `${member.user.full_name} removed`, variant: "success" });
      load();
    } catch (error) {
      toast({
        title: "Could not remove member",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    } finally {
      setRemovingId(null);
      setConfirmRemove(null);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Users</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage who has access to <strong>{activeWorkspace?.name}</strong> and what they can do.
          </p>
        </div>
        {canManage && (
          <Button onClick={() => setInviteOpen(true)}>
            <UserPlus className="h-4 w-4" />
            Invite member
          </Button>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Members</CardTitle>
          <CardDescription>{members.length} people in this workspace</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[0, 1, 2].map((i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="h-9 w-9 rounded-full" />
                  <div className="flex-1 space-y-1.5">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {members.map((member) => (
                <li key={member.user.id} className="flex items-center gap-3 py-3">
                  <Avatar name={member.user.full_name} />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium">{member.user.full_name}</p>
                    <p className="truncate text-xs text-muted-foreground">
                      {member.user.email} · joined {formatDate(member.joined_at)}
                    </p>
                  </div>
                  <Badge variant={roleBadge[member.role] ?? "secondary"}>{member.role}</Badge>

                  {canManage && (
                    <Dropdown
                      trigger={
                        <button className="cursor-pointer rounded-md px-2 py-1 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground">
                          Manage ▾
                        </button>
                      }
                      width="min-w-[10rem]"
                    >
                      {(close) => (
                        <>
                          {ROLES.filter((r) => r !== member.role).map((role) => (
                            <DropdownItem
                              key={role}
                              onClick={() => {
                                changeRole(member, role);
                                close();
                              }}
                            >
                              Set {role}
                            </DropdownItem>
                          ))}
                          <div className="my-1 h-px bg-border" />
                          <DropdownItem
                            danger
                            onClick={() => {
                              setConfirmRemove(member.user.id);
                              close();
                            }}
                          >
                            <UserMinus className="h-4 w-4" />
                            Remove
                          </DropdownItem>
                        </>
                      )}
                    </Dropdown>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Modal
        open={inviteOpen}
        onClose={() => setInviteOpen(false)}
        title="Invite a member"
        description="The person must already have a TenantDesk account."
      >
        <div className="space-y-4">
          <div>
            <Label htmlFor="invite-email">Email</Label>
            <Input
              id="invite-email"
              type="email"
              placeholder="teammate@company.com"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="invite-role">Role</Label>
            <select
              id="invite-role"
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="flex h-10 w-full cursor-pointer rounded-md border border-input bg-card px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {ROLES.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-muted-foreground">
              owner &gt; admin &gt; manager &gt; agent &gt; user
            </p>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={() => setInviteOpen(false)}>
              Cancel
            </Button>
            <Button onClick={invite} disabled={inviting || !inviteEmail.trim()}>
              {inviting && <Spinner />}
              Send invite
            </Button>
          </div>
        </div>
      </Modal>

      <Modal
        open={confirmRemove !== null}
        onClose={() => setConfirmRemove(null)}
        title="Remove member?"
        description="They will lose access to this workspace immediately."
      >
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" onClick={() => setConfirmRemove(null)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={() => {
              const member = members.find((m) => m.user.id === confirmRemove);
              if (member) remove(member);
            }}
            disabled={removingId !== null}
          >
            {removingId !== null && <Loader2 className="h-4 w-4 animate-spin" />}
            Remove member
          </Button>
        </div>
      </Modal>
    </div>
  );
}
