"use client";

import { useState } from "react";
import { Check, Clock, Mail, MessageSquare, Send, Sparkles } from "lucide-react";

import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

const CHANNELS = [
  {
    icon: MessageSquare,
    title: "Community",
    detail: "Questions, ideas and help from other builders.",
    action: "Join the conversation",
  },
  {
    icon: Mail,
    title: "Email",
    detail: "Sales, partnerships and billing questions.",
    action: "support@tenantdesk.example",
  },
  {
    icon: Clock,
    title: "Response time",
    detail: "We reply to every message within one business day.",
    action: "Mon–Fri, 9:00–18:00",
  },
];

export default function ContactPage() {
  const [sent, setSent] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="mx-auto max-w-6xl px-4 pb-20 pt-14 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <Badge variant="secondary">
            <Sparkles className="h-3.5 w-3.5" /> We&apos;d love to hear from you
          </Badge>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">Contact us</h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Questions about the platform, plans or deploying TenantDesk AI? Send us a message
            and we&apos;ll get back to you within one business day.
          </p>
        </div>

        <div className="mt-12 grid gap-6 lg:grid-cols-5">
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>Send a message</CardTitle>
              <CardDescription>We reply to every message — no ticket bots here.</CardDescription>
            </CardHeader>
            <CardContent>
              {sent ? (
                <div className="flex flex-col items-center gap-3 py-10 text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-success/15 text-success">
                    <Check className="h-6 w-6" />
                  </div>
                  <p className="font-medium">Message received!</p>
                  <p className="text-sm text-muted-foreground">
                    Thanks for reaching out — we&apos;ll get back to you shortly.
                  </p>
                </div>
              ) : (
                <form
                  className="space-y-4"
                  onSubmit={(e) => {
                    e.preventDefault();
                    setSent(true);
                  }}
                >
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <Label htmlFor="name">Name</Label>
                      <Input id="name" placeholder="Ada Lovelace" required />
                    </div>
                    <div>
                      <Label htmlFor="email">Work email</Label>
                      <Input id="email" type="email" placeholder="you@company.com" required />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="subject">Subject</Label>
                    <Input id="subject" placeholder="How can we help?" required />
                  </div>
                  <div>
                    <Label htmlFor="message">Message</Label>
                    <Textarea
                      id="message"
                      rows={6}
                      placeholder="Tell us about your use case, timeline and team size…"
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full sm:w-auto">
                    <Send className="h-4 w-4" />
                    Send message
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>

          <div className="space-y-4 lg:col-span-2">
            {CHANNELS.map((channel) => (
              <Card key={channel.title}>
                <CardContent className="flex items-start gap-4 p-5">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <channel.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-medium">{channel.title}</p>
                    <p className="mt-0.5 text-sm text-muted-foreground">{channel.detail}</p>
                    <p className="mt-1.5 text-sm font-medium text-primary">{channel.action}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
