import { ComponentRegistry } from '../src/design-system/registry/components';

function validateRegistry() {
  let errors = 0;
  for (const [key, meta] of Object.entries(ComponentRegistry)) {
    if (!meta.id || !meta.version || !meta.category || !meta.maturity) {
      console.error(`Invalid metadata for component ${key}`);
      errors++;
    }
  }
  if (errors > 0) {
    console.error('Validation failed!');
    process.exit(1);
  } else {
    console.log('Validation passed!');
  }
}

validateRegistry();
