import { z, defineCollection } from 'astro:content';

const resourcesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    grade: z.string(),
    subject: z.string(),
    brand: z.string(),
    type: z.string(),
    link: z.string(),
    tags: z.array(z.string()).optional().default([]),
    description: z.string().optional().default(''),
  }),
});

export const collections = {
  resources: resourcesCollection,
};
